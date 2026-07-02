from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.slug import make_slug
from app.models.product import Product, ProductCategory, ProductMaterial
from app.schemas.product import CompositionItem, ProductCreate, ProductUpdate

# Полная загрузка связей (состав с материалами + фото), чтобы избежать
# ленивой подгрузки в async-контексте (MissingGreenlet).
_WITH_RELATIONS = (
    selectinload(Product.composition).selectinload(ProductMaterial.material),
    selectinload(Product.images),
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
        .options(*_WITH_RELATIONS)
        .execution_options(populate_existing=True)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get(session: AsyncSession, product_id: int) -> Product | None:
    return await _get_full(session, product_id)


async def get_by_slug(session: AsyncSession, slug: str) -> Product | None:
    stmt = select(Product).where(Product.slug == slug).options(*_WITH_RELATIONS)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: ProductCategory | None = None,
) -> list[Product]:
    stmt = select(Product).options(*_WITH_RELATIONS)
    if category is not None:
        stmt = stmt.where(Product.category == category)
    result = await session.execute(stmt.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(session: AsyncSession, data: ProductCreate) -> Product:
    payload = data.model_dump(exclude={"composition"})
    product = Product(**payload, composition=_build_composition(data.composition))
    session.add(product)
    await session.flush()  # получаем id для номера в слаге
    product.slug = make_slug(product.name, product.id)
    await session.commit()
    return await _get_full(session, product.id)


async def update(
    session: AsyncSession, product: Product, data: ProductUpdate
) -> Product:
    payload = data.model_dump(exclude_unset=True, exclude={"composition"})
    for field, value in payload.items():
        setattr(product, field, value)
    # При переименовании держим слаг в синхроне с названием (номер = id).
    if "name" in payload:
        product.slug = make_slug(product.name, product.id)
    if data.composition is not None:
        product.composition = _build_composition(data.composition)
    await session.commit()
    return await _get_full(session, product.id)


async def delete(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()
