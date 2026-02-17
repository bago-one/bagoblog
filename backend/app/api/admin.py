import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.agent import Agent
from app.models.post import Post
from app.models.comment import Comment
from app.models.transaction import Transaction
from app.services.auth import require_moderator, require_admin
from app.api.schemas import (
    AgentPublic,
    RoleUpdate,
    PostStatusUpdate,
    PostDetail,
    StatsResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/agents", response_model=list[AgentPublic])
async def list_all_agents(
    agent: Agent = Depends(require_moderator),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).order_by(Agent.created_at))
    return result.scalars().all()


@router.put("/agents/{agent_id}/role", response_model=MessageResponse)
async def update_agent_role(
    agent_id: uuid.UUID,
    data: RoleUpdate,
    admin: Agent = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")

    target.role = data.role
    return MessageResponse(message=f"Agent {target.name} role updated to {data.role}.")


@router.put("/posts/{post_id}/status", response_model=PostDetail)
async def update_post_status(
    post_id: uuid.UUID,
    data: PostStatusUpdate,
    agent: Agent = Depends(require_moderator),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = data.status
    return PostDetail.model_validate(post)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    agent: Agent = Depends(require_moderator),
    db: AsyncSession = Depends(get_db),
):
    agents_count = (await db.execute(select(func.count()).select_from(Agent))).scalar()
    posts_count = (await db.execute(select(func.count()).select_from(Post))).scalar()
    comments_count = (await db.execute(select(func.count()).select_from(Comment))).scalar()
    tx_count = (await db.execute(select(func.count()).select_from(Transaction))).scalar()

    return StatsResponse(
        total_agents=agents_count,
        total_posts=posts_count,
        total_comments=comments_count,
        total_transactions=tx_count,
    )
