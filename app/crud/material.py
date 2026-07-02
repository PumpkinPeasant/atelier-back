from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate


async def get(session: AsyncSession, material_id: int) -> Material | None:
    return await session.get(Material, material_id)


async def list_(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Material]:
    result = await session.execute(select(Material).offset(skip).limit(limit))
    return list(result.scalars().all())


async def existing_ids(session: AsyncSession, ids: list[int]) -> set[int]:
    if not ids:
        return set()
    result = await session.execute(select(Material.id).where(Material.id.in_(ids)))
    return set(result.scalars().all())


async def create(session: AsyncSession, data: MaterialCreate) -> Material:
    material = Material(**data.model_dump())
    session.add(material)
    await session.commit()
    await session.refresh(material)
    return material


async def update(
    session: AsyncSession, material: Material, data: MaterialUpdate
) -> Material:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(material, field, value)
    await session.commit()
    await session.refresh(material)
    return material


async def delete(session: AsyncSession, material: Material) -> None:
    await session.delete(material)
    await session.commit()
