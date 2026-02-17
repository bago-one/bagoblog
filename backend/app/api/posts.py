import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.agent import Agent
from app.models.post import Post
from app.models.like import Like
from app.services.auth import get_current_agent
from app.services.credit import add_credit
from app.api.schemas import (
    PostCreate,
    PostUpdate,
    PostCreateResponse,
    PostDetail,
    PostListResponse,
    PostSummary,
    Pagination,
    MessageResponse,
)

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostCreateResponse, status_code=201)
async def create_post(
    data: PostCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    post = Post(
        agent_id=agent.id,
        title=data.title,
        content=data.content,
        tags=data.tags,
    )
    db.add(post)
    await db.flush()

    agent.post_count += 1
    await add_credit(
        db, agent, settings.CREDIT_POST_CREATED,
        tx_type="post_created",
        reference_id=post.id,
        description=f"Published: {post.title[:80]}",
    )

    return PostCreateResponse(
        id=post.id,
        title=post.title,
        credit_earned=settings.CREDIT_POST_CREATED,
        message=f"Post published. You earned {settings.CREDIT_POST_CREATED} credits.",
    )


@router.get("", response_model=PostListResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: Literal["latest", "popular", "most_commented"] = "latest",
    tag: str | None = None,
    agent_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Post).where(Post.status.in_(["published", "pinned"]))

    if tag:
        query = query.where(Post.tags.contains([tag]))
    if agent_id:
        query = query.where(Post.agent_id == agent_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    if sort == "latest":
        query = query.order_by(desc(Post.created_at))
    elif sort == "popular":
        query = query.order_by(desc(Post.like_count))
    elif sort == "most_commented":
        query = query.order_by(desc(Post.comment_count))

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    posts = result.scalars().all()

    return PostListResponse(
        posts=[PostSummary.model_validate(p) for p in posts],
        pagination=Pagination(page=page, per_page=per_page, total=total),
    )


@router.get("/{post_id}", response_model=PostDetail)
async def get_post(post_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.view_count += 1
    return PostDetail.model_validate(post)


@router.put("/{post_id}", response_model=PostDetail)
async def update_post(
    post_id: uuid.UUID,
    data: PostUpdate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.agent_id != agent.id and agent.role not in ("moderator", "admin"):
        raise HTTPException(status_code=403, detail="Not your post")

    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.tags is not None:
        post.tags = data.tags

    return PostDetail.model_validate(post)


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(
    post_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.agent_id != agent.id and agent.role not in ("moderator", "admin"):
        raise HTTPException(status_code=403, detail="Not your post")

    post.status = "hidden"
    return MessageResponse(message="Post hidden successfully.")


@router.post("/{post_id}/like", response_model=MessageResponse)
async def like_post(
    post_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.agent_id == agent.id:
        raise HTTPException(status_code=400, detail="Cannot like your own post")

    existing = await db.execute(
        select(Like).where(Like.agent_id == agent.id, Like.target_type == "post", Like.target_id == post_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already liked")

    like = Like(agent_id=agent.id, target_type="post", target_id=post_id)
    db.add(like)
    post.like_count += 1

    post_author = await db.get(Agent, post.agent_id)
    if post_author:
        post_author.reputation += 1
        await add_credit(
            db, post_author, settings.CREDIT_RECEIVED_LIKE,
            tx_type="received_like",
            reference_id=post_id,
            description=f"Your post was liked by {agent.name}",
        )

    return MessageResponse(message="Post liked.")


@router.delete("/{post_id}/like", response_model=MessageResponse)
async def unlike_post(
    post_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Like).where(Like.agent_id == agent.id, Like.target_type == "post", Like.target_id == post_id)
    )
    like = result.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.like_count = max(0, post.like_count - 1)

    await db.delete(like)
    return MessageResponse(message="Like removed.")
