from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import ProductImage


async def get(session: AsyncSession, image_id: int) -> ProductImage | None:
    return await session.get(ProductImage, image_id)


async def list_for_product(
    session: AsyncSession, product_id: int
) -> list[ProductImage]:
    result = await session.execute(
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
    )
    return list(result.scalars().all())


async def create(
    session: AsyncSession,
    product_id: int,
    key: str,
    url: str,
    is_main: bool = False,
) -> ProductImage:
    if is_main:
        # Главное фото — только одно на товар.
        await session.execute(
            update(ProductImage)
            .where(ProductImage.product_id == product_id)
            .values(is_main=False)
        )

    max_order = await session.scalar(
        select(func.coalesce(func.max(ProductImage.sort_order), -1)).where(
            ProductImage.product_id == product_id
        )
    )
    image = ProductImage(
        product_id=product_id,
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
