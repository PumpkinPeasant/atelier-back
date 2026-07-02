from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

_ORDER = (Category.sort_order, Category.name)


async def get(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def list_(
    session: AsyncSession, group_id: int | None = None
) -> list[Category]:
    stmt = select(Category).order_by(*_ORDER)
    if group_id is not None:
        stmt = stmt.where(Category.group_id == group_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create(session: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update(
    session: AsyncSession, category: Category, data: CategoryUpdate
) -> Category:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    await session.commit()
    await session.refresh(category)
    return category


async def delete(session: AsyncSession, category: Category) -> None:
    await session.delete(category)
    await session.commit()
