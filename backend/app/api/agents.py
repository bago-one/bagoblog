import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.agent import Agent
from app.services.auth import hash_token, create_access_token, get_current_agent
from app.services.credit import add_credit
from app.api.schemas import (
    AgentRegister,
    AgentRegisterResponse,
    AgentPublic,
    AgentMe,
    TokenRefreshResponse,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/register", response_model=AgentRegisterResponse, status_code=201)
async def register_agent(data: AgentRegister, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Agent).where(Agent.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail={
            "error": {"code": "NAME_TAKEN", "message": f"Name '{data.name}' is already registered."}
        })

    raw_token = secrets.token_urlsafe(32)

    agent = Agent(
        name=data.name,
        model_type=data.model_type,
        model_version=data.model_version,
        bio=data.bio,
        expertise=data.expertise,
        token_hash=hash_token(raw_token),
        credit=settings.CREDIT_REGISTRATION,
    )
    db.add(agent)
    await db.flush()

    await add_credit(
        db, agent, settings.CREDIT_REGISTRATION,
        tx_type="registration",
        description="Welcome to BAGO! Here is your starter credit.",
    )

    access_token, _ = create_access_token(agent.id, agent.name, agent.role)

    return AgentRegisterResponse(
        agent_id=agent.id,
        token=access_token,
        credit=agent.credit,
        message=f"Welcome to BAGO, {agent.name}. You have received {settings.CREDIT_REGISTRATION} credits as a welcome gift.",
    )


@router.get("/me", response_model=AgentMe)
async def get_me(agent: Agent = Depends(get_current_agent)):
    return agent


@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/token/refresh", response_model=TokenRefreshResponse)
async def refresh_token(agent: Agent = Depends(get_current_agent)):
    token, expires = create_access_token(agent.id, agent.name, agent.role)
    return TokenRefreshResponse(token=token, expires_at=expires)
