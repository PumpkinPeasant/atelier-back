from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductCategory, ProductMaterial
from app.schemas.product import CompositionItem, ProductCreate, ProductUpdate

# Полная загрузка состава вместе с материалами, чтобы избежать ленивой
# подгрузки в async-контексте (MissingGreenlet).
_WITH_COMPOSITION = selectinload(Product.composition).selectinload(
    ProductMaterial.material
)


def _build_composition(items: list[CompositionItem]) -> list[ProductMaterial]:
    return [
        ProductMaterial(material_id=item.material_id, percent=item.percent)
        for item in items
    ]


async def _get_full(session: AsyncSession, product_id: int) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(_WITH_COMPOSITION)
        .execution_options(populate_existing=True)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get(session: AsyncSession, product_id: int) -> Product | None:
    return await _get_full(session, product_id)


async def list_(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: ProductCategory | None = None,
) -> list[Product]:
    stmt = select(Product).options(_WITH_COMPOSITION)
    if category is not None:
        stmt = stmt.where(Product.category == category)
    result = await session.execute(stmt.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(session: AsyncSession, data: ProductCreate) -> Product:
    payload = data.model_dump(exclude={"composition"})
    product = Product(**payload, composition=_build_composition(data.composition))
    session.add(product)
    await session.commit()
    return await _get_full(session, product.id)


async def update(
    session: AsyncSession, product: Product, data: ProductUpdate
) -> Product:
    payload = data.model_dump(exclude_unset=True, exclude={"composition"})
    for field, value in payload.items():
        setattr(product, field, value)
    if data.composition is not None:
        product.composition = _build_composition(data.composition)
    await session.commit()
    return await _get_full(session, product.id)


async def delete(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()
