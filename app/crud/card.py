from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.slug import make_slug
from app.models.card import CardStatus, ProductCard
from app.models.product import Product, ProductMaterial, ProductVariant
from app.schemas.card import ProductCardCreate, ProductCardUpdate

# Карточка отдаётся вместе с фото и полными бизнес-данными товара
# (состав + варианты с цветом/размером).
_WITH_RELATIONS = (
    selectinload(ProductCard.images),
    # Вложенный product сериализуется как ProductRead и обращается к product.card
    # (CardBrief) — грузим её эагерно, иначе ленивый IO в async (MissingGreenlet).
    selectinload(ProductCard.product).selectinload(Product.card),
    selectinload(ProductCard.product)
    .selectinload(Product.composition)
    .selectinload(ProductMaterial.material),
    selectinload(ProductCard.product)
    .selectinload(Product.variants)
    .selectinload(ProductVariant.color),
    selectinload(ProductCard.product)
    .selectinload(Product.variants)
    .selectinload(ProductVariant.size),
)


def _card_slug(card: ProductCard, product: Product) -> str:
    """Слаг из заголовка карточки (или имени товара) и её номера."""
    return make_slug(card.title or product.name, card.id)


async def _get_full(session: AsyncSession, card_id: int) -> ProductCard | None:
    stmt = (
        select(ProductCard)
        .where(ProductCard.id == card_id)
        .options(*_WITH_RELATIONS)
        .execution_options(populate_existing=True)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get(session: AsyncSession, card_id: int) -> ProductCard | None:
    return await _get_full(session, card_id)


async def get_by_product(
    session: AsyncSession, product_id: int
) -> ProductCard | None:
    stmt = select(ProductCard).where(ProductCard.product_id == product_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_slug(session: AsyncSession, slug: str) -> ProductCard | None:
    stmt = (
        select(ProductCard).where(ProductCard.slug == slug).options(*_WITH_RELATIONS)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: CardStatus | None = None,
) -> list[ProductCard]:
    stmt = select(ProductCard).options(*_WITH_RELATIONS)
    if status is not None:
        stmt = stmt.where(ProductCard.status == status)
    result = await session.execute(stmt.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(
    session: AsyncSession, product: Product, data: ProductCardCreate
) -> ProductCard:
    card = ProductCard(
        product_id=product.id,
        title=data.title,
        description=data.description,
        price=data.price,
        status=CardStatus.DRAFT,
    )
    session.add(card)
    await session.flush()  # получаем id для номера в слаге
    card.slug = _card_slug(card, product)
    await session.commit()
    return await _get_full(session, card.id)


async def update(
    session: AsyncSession, card: ProductCard, data: ProductCardUpdate
) -> ProductCard:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(card, field, value)
    # При смене заголовка держим слаг в синхроне (номер = id карточки).
    if "title" in payload:
        card.slug = _card_slug(card, card.product)
    await session.commit()
    return await _get_full(session, card.id)


async def set_status(
    session: AsyncSession, card: ProductCard, status: CardStatus
) -> ProductCard:
    card.status = status
    if status == CardStatus.PUBLISHED:
        # Колонка naive (как и created_at через server_default now()); пишем UTC.
        card.published_at = datetime.utcnow()
    await session.commit()
    return await _get_full(session, card.id)


async def delete(session: AsyncSession, card: ProductCard) -> None:
    await session.delete(card)
    await session.commit()
