from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


async def get(session: AsyncSession, order_id: int) -> Order | None:
    return await session.get(Order, order_id)


async def list_(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    client_id: int | None = None,
) -> list[Order]:
    stmt = select(Order)
    if client_id is not None:
        stmt = stmt.where(Order.client_id == client_id)
    result = await session.execute(stmt.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(session: AsyncSession, data: OrderCreate) -> Order:
    order = Order(**data.model_dump())
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def update(session: AsyncSession, order: Order, data: OrderUpdate) -> Order:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    await session.commit()
    await session.refresh(order)
    return order


async def delete(session: AsyncSession, order: Order) -> None:
    await session.delete(order)
    await session.commit()
