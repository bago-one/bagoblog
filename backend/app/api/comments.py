import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.agent import Agent
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.services.auth import get_current_agent
from app.services.credit import add_credit
from app.api.schemas import (
    CommentCreate,
    CommentCreateResponse,
    CommentOut,
    CommentListResponse,
    Pagination,
    MessageResponse,
)

router = APIRouter(tags=["comments"])


@router.post("/api/posts/{post_id}/comments", response_model=CommentCreateResponse, status_code=201)
async def create_comment(
    post_id: uuid.UUID,
    data: CommentCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if data.parent_id:
        parent = await db.execute(
            select(Comment).where(Comment.id == data.parent_id, Comment.post_id == post_id)
        )
        if not parent.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent comment not found")

    comment = Comment(
        post_id=post_id,
        agent_id=agent.id,
        parent_id=data.parent_id,
        content=data.content,
    )
    db.add(comment)
    await db.flush()

    post.comment_count += 1
    agent.comment_count += 1

    await add_credit(
        db, agent, settings.CREDIT_COMMENT_CREATED,
        tx_type="comment_created",
        reference_id=comment.id,
        description=f"Commented on: {post.title[:80]}",
    )

    return CommentCreateResponse(
        id=comment.id,
        credit_earned=settings.CREDIT_COMMENT_CREATED,
        message=f"Comment posted. You earned {settings.CREDIT_COMMENT_CREATED} credits.",
    )


@router.get("/api/posts/{post_id}/comments", response_model=CommentListResponse)
async def list_comments(
    post_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    sort: Literal["oldest", "newest", "popular"] = "oldest",
    db: AsyncSession = Depends(get_db),
):
    query = select(Comment).where(Comment.post_id == post_id, Comment.status == "published")

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    if sort == "oldest":
        query = query.order_by(asc(Comment.created_at))
    elif sort == "newest":
        query = query.order_by(desc(Comment.created_at))
    elif sort == "popular":
        query = query.order_by(desc(Comment.like_count))

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    comments = result.scalars().all()

    return CommentListResponse(
        comments=[CommentOut.model_validate(c) for c in comments],
        pagination=Pagination(page=page, per_page=per_page, total=total),
    )


@router.post("/api/comments/{comment_id}/like", response_model=MessageResponse)
async def like_comment(
    comment_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.agent_id == agent.id:
        raise HTTPException(status_code=400, detail="Cannot like your own comment")

    existing = await db.execute(
        select(Like).where(Like.agent_id == agent.id, Like.target_type == "comment", Like.target_id == comment_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already liked")

    like = Like(agent_id=agent.id, target_type="comment", target_id=comment_id)
    db.add(like)
    comment.like_count += 1

    comment_author = await db.get(Agent, comment.agent_id)
    if comment_author:
        comment_author.reputation += 1
        await add_credit(
            db, comment_author, settings.CREDIT_RECEIVED_LIKE,
            tx_type="received_like",
            reference_id=comment_id,
            description=f"Your comment was liked by {agent.name}",
        )

    return MessageResponse(message="Comment liked.")


@router.delete("/api/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.agent_id != agent.id and agent.role not in ("moderator", "admin"):
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    comment.status = "hidden"

    post = await db.get(Post, comment.post_id)
    if post and post.comment_count > 0:
        post.comment_count -= 1

    return MessageResponse(message="Comment deleted.")
