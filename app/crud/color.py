from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.color import Color
from app.schemas.lookup import ColorCreate, ColorUpdate


async def get(session: AsyncSession, color_id: int) -> Color | None:
    return await session.get(Color, color_id)


async def list_(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Color]:
    result = await session.execute(
        select(Color).order_by(Color.name).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def search(
    session: AsyncSession, q: str | None = None, limit: int = 20
) -> list[Color]:
    stmt = select(Color).order_by(Color.name)
    if q:
        stmt = stmt.where(Color.name.ilike(f"%{q}%"))
    result = await session.execute(stmt.limit(limit))
    return list(result.scalars().all())


async def create(session: AsyncSession, data: ColorCreate) -> Color:
    color = Color(**data.model_dump())
    session.add(color)
    await session.commit()
    await session.refresh(color)
    return color


async def update(session: AsyncSession, color: Color, data: ColorUpdate) -> Color:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(color, field, value)
    await session.commit()
    await session.refresh(color)
    return color


async def delete(session: AsyncSession, color: Color) -> None:
    await session.delete(color)
    await session.commit()
