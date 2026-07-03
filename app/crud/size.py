from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.size import Size
from app.schemas.lookup import SizeCreate, SizeUpdate

_ORDER = (Size.sort_order, Size.name)


async def get(session: AsyncSession, size_id: int) -> Size | None:
    return await session.get(Size, size_id)


async def list_(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Size]:
    result = await session.execute(
        select(Size).order_by(*_ORDER).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def search(
    session: AsyncSession, q: str | None = None, limit: int = 20
) -> list[Size]:
    stmt = select(Size).order_by(*_ORDER)
    if q:
        stmt = stmt.where(Size.name.ilike(f"%{q}%"))
    result = await session.execute(stmt.limit(limit))
    return list(result.scalars().all())


async def existing_ids(session: AsyncSession, ids: set[int]) -> set[int]:
    if not ids:
        return set()
    result = await session.execute(select(Size.id).where(Size.id.in_(ids)))
    return set(result.scalars().all())


async def create(session: AsyncSession, data: SizeCreate) -> Size:
    size = Size(**data.model_dump())
    session.add(size)
    await session.commit()
    await session.refresh(size)
    return size


async def update(session: AsyncSession, size: Size, data: SizeUpdate) -> Size:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(size, field, value)
    await session.commit()
    await session.refresh(size)
    return size


async def delete(session: AsyncSession, size: Size) -> None:
    await session.delete(size)
    await session.commit()
