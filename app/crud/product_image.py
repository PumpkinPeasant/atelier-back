from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import ProductImage


async def get(session: AsyncSession, image_id: int) -> ProductImage | None:
    return await session.get(ProductImage, image_id)


async def list_for_card(session: AsyncSession, card_id: int) -> list[ProductImage]:
    result = await session.execute(
        select(ProductImage)
        .where(ProductImage.card_id == card_id)
        .order_by(ProductImage.sort_order)
    )
    return list(result.scalars().all())


async def create(
    session: AsyncSession,
    card_id: int,
    key: str,
    url: str,
    is_main: bool = False,
    color_id: int | None = None,
) -> ProductImage:
    if is_main:
        # Главное фото — только одно на карточку.
        await session.execute(
            update(ProductImage)
            .where(ProductImage.card_id == card_id)
            .values(is_main=False)
        )

    max_order = await session.scalar(
        select(func.coalesce(func.max(ProductImage.sort_order), -1)).where(
            ProductImage.card_id == card_id
        )
    )
    image = ProductImage(
        card_id=card_id,
        color_id=color_id,
        key=key,
        url=url,
        is_main=is_main,
        sort_order=(max_order or -1) + 1,
    )
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


async def delete(session: AsyncSession, image: ProductImage) -> None:
    await session.delete(image)
    await session.commit()
