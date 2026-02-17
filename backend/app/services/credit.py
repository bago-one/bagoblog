import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.agent import Agent
from app.models.transaction import Transaction


async def add_credit(
    db: AsyncSession,
    agent: Agent,
    amount: int,
    tx_type: str,
    reference_id: uuid.UUID | None = None,
    description: str | None = None,
) -> Transaction:
    agent.credit += amount
    new_balance = agent.credit

    tx = Transaction(
        agent_id=agent.id,
        amount=amount,
        balance_after=new_balance,
        type=tx_type,
        reference_id=reference_id,
        description=description,
    )
    db.add(tx)
    return tx


async def get_wallet_summary(db: AsyncSession, agent_id: uuid.UUID) -> dict:
    earned = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.agent_id == agent_id, Transaction.amount > 0)
    )
    spent = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.agent_id == agent_id, Transaction.amount < 0)
    )
    total_earned = earned.scalar()
    total_spent = abs(spent.scalar())
    return {"total_earned": total_earned, "total_spent": total_spent}
