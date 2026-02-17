import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.agent import Agent

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_token(token: str) -> str:
    return pwd_context.hash(token)


def verify_token_hash(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(agent_id: uuid.UUID, name: str, role: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRE_DAYS)
    payload = {
        "agent_id": str(agent_id),
        "name": name,
        "role": role,
        "exp": expires,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, expires


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Token is invalid or expired."}},
        )


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    payload = decode_access_token(credentials.credentials)
    agent_id = payload.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(Agent).where(Agent.id == uuid.UUID(agent_id)))
    agent = result.scalar_one_or_none()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=401, detail="Agent not found or inactive")

    return agent


async def require_role(role: str, agent: Agent = Depends(get_current_agent)) -> Agent:
    role_hierarchy = {"member": 0, "moderator": 1, "admin": 2}
    if role_hierarchy.get(agent.role, 0) < role_hierarchy.get(role, 0):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return agent


def require_moderator(agent: Agent = Depends(get_current_agent)) -> Agent:
    role_hierarchy = {"member": 0, "moderator": 1, "admin": 2}
    if role_hierarchy.get(agent.role, 0) < 1:
        raise HTTPException(status_code=403, detail="Moderator or admin role required")
    return agent


def require_admin(agent: Agent = Depends(get_current_agent)) -> Agent:
    if agent.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return agent
