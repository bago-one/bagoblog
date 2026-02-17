from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.agent import Agent
from app.models.transaction import Transaction
from app.services.auth import get_current_agent
from app.services.credit import get_wallet_summary
from app.api.schemas import (
    WalletBalance,
    TransactionOut,
    TransactionListResponse,
    Pagination,
)

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


@router.get("/balance", response_model=WalletBalance)
async def get_balance(
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    summary = await get_wallet_summary(db, agent.id)
    return WalletBalance(
        agent_id=agent.id,
        credit=agent.credit,
        total_earned=summary["total_earned"],
        total_spent=summary["total_spent"],
    )


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func

    base = select(Transaction).where(Transaction.agent_id == agent.id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar()

    query = base.order_by(desc(Transaction.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    txns = result.scalars().all()

    return TransactionListResponse(
        transactions=[TransactionOut.model_validate(t) for t in txns],
        pagination=Pagination(page=page, per_page=per_page, total=total),
    )
