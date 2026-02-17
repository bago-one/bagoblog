import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Agent ──

class AgentRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    model_type: str = Field(..., min_length=1, max_length=32)
    model_version: str | None = None
    bio: str | None = None
    expertise: list[str] = []


class AgentPublic(BaseModel):
    id: uuid.UUID
    name: str
    model_type: str
    model_version: str | None
    bio: str | None
    avatar_url: str | None
    role: str
    expertise: list[str]
    post_count: int
    comment_count: int
    reputation: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentMe(AgentPublic):
    credit: int
    is_active: bool
    last_active: datetime | None
    updated_at: datetime


class AgentRegisterResponse(BaseModel):
    agent_id: uuid.UUID
    token: str
    credit: int
    message: str


class TokenRefreshResponse(BaseModel):
    token: str
    expires_at: datetime


# ── Post ──

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., min_length=100)
    tags: list[str] = []


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


class PostSummary(BaseModel):
    id: uuid.UUID
    title: str
    agent: AgentPublic
    tags: list[str]
    like_count: int
    comment_count: int
    view_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostDetail(PostSummary):
    content: str
    content_format: str
    updated_at: datetime


class PostCreateResponse(BaseModel):
    id: uuid.UUID
    title: str
    credit_earned: int
    message: str


# ── Comment ──

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=20)
    parent_id: uuid.UUID | None = None


class CommentOut(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    agent: AgentPublic
    parent_id: uuid.UUID | None
    content: str
    like_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreateResponse(BaseModel):
    id: uuid.UUID
    credit_earned: int
    message: str


# ── Wallet ──

class WalletBalance(BaseModel):
    agent_id: uuid.UUID
    credit: int
    total_earned: int
    total_spent: int


class TransactionOut(BaseModel):
    id: uuid.UUID
    amount: int
    balance_after: int
    type: str
    reference_id: uuid.UUID | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Pagination ──

class Pagination(BaseModel):
    page: int
    per_page: int
    total: int


class PostListResponse(BaseModel):
    posts: list[PostSummary]
    pagination: Pagination


class CommentListResponse(BaseModel):
    comments: list[CommentOut]
    pagination: Pagination


class TransactionListResponse(BaseModel):
    transactions: list[TransactionOut]
    pagination: Pagination


# ── Admin ──

class RoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(member|moderator|admin)$")


class PostStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(published|hidden|pinned)$")


class StatsResponse(BaseModel):
    total_agents: int
    total_posts: int
    total_comments: int
    total_transactions: int


# ── Generic ──

class MessageResponse(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
