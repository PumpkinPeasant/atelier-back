from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import CategoryGroup
from app.schemas.category import CategoryGroupCreate, CategoryGroupUpdate

_ORDER = (CategoryGroup.sort_order, CategoryGroup.name)


async def get(session: AsyncSession, group_id: int) -> CategoryGroup | None:
    return await session.get(CategoryGroup, group_id)


async def list_(session: AsyncSession) -> list[CategoryGroup]:
    """Список групп вместе с категориями (categories грузятся через selectin)."""
    result = await session.execute(select(CategoryGroup).order_by(*_ORDER))
    return list(result.scalars().all())


async def create(
    session: AsyncSession, data: CategoryGroupCreate
) -> CategoryGroup:
    group = CategoryGroup(**data.model_dump())
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group


async def update(
    session: AsyncSession, group: CategoryGroup, data: CategoryGroupUpdate
) -> CategoryGroup:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    await session.commit()
    await session.refresh(group)
    return group


async def delete(session: AsyncSession, group: CategoryGroup) -> None:
    await session.delete(group)
    await session.commit()
