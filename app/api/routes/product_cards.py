from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.api.deps import SessionDep
from app.core import storage
from app.crud import card as crud
from app.crud import color as color_crud
from app.crud import product as product_crud
from app.crud import product_image as image_crud
from app.models.card import CardStatus
from app.schemas.card import (
    ProductCardCreate,
    ProductCardRead,
    ProductCardUpdate,
)
from app.schemas.card import ProductImageRead

router = APIRouter(prefix="/product-cards", tags=["product-cards"])

# Разрешённые типы изображений и максимальный размер файла.
_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


async def _get_or_404(session: SessionDep, card_id: int):
    card = await crud.get(session, card_id)
    if card is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Card not found")
    return card


@router.get("", response_model=list[ProductCardRead])
async def list_cards(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    status_filter: CardStatus | None = None,
):
    return await crud.list_(session, skip=skip, limit=limit, status=status_filter)


@router.post("", response_model=ProductCardRead, status_code=status.HTTP_201_CREATED)
async def create_card(payload: ProductCardCreate, session: SessionDep):
    product = await product_crud.get(session, payload.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    if await crud.get_by_product(session, payload.product_id) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Product already has a card"
        )
    return await crud.create(session, product, payload)


@router.get("/{card_id}", response_model=ProductCardRead)
async def get_card(card_id: int, session: SessionDep):
    return await _get_or_404(session, card_id)


@router.patch("/{card_id}", response_model=ProductCardRead)
async def update_card(card_id: int, payload: ProductCardUpdate, session: SessionDep):
    card = await _get_or_404(session, card_id)
    return await crud.update(session, card, payload)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int, session: SessionDep):
    card = await _get_or_404(session, card_id)
    # Удаляем файлы из S3 до удаления карточки (фото уйдут по каскаду).
    for image in card.images:
        await run_in_threadpool(storage.delete_object, image.key)
    await crud.delete(session, card)


@router.post("/{card_id}/publish", response_model=ProductCardRead)
async def publish_card(card_id: int, session: SessionDep):
    card = await _get_or_404(session, card_id)
    return await crud.set_status(session, card, CardStatus.PUBLISHED)


@router.post("/{card_id}/unpublish", response_model=ProductCardRead)
async def unpublish_card(card_id: int, session: SessionDep):
    card = await _get_or_404(session, card_id)
    return await crud.set_status(session, card, CardStatus.DRAFT)


@router.post(
    "/{card_id}/images",
    response_model=ProductImageRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_card_image(
    card_id: int,
    session: SessionDep,
    file: UploadFile = File(...),
    is_main: bool = Form(False),
    color_id: int | None = Form(None),
):
    card = await _get_or_404(session, card_id)

    if color_id is not None and await color_crud.get(session, color_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Color not found")

    ext = _IMAGE_EXTENSIONS.get(file.content_type or "")
    if ext is None:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Only JPEG, PNG or WEBP images are allowed",
        )

    data = await file.read()
    if len(data) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image is too large (max 10 MB)"
        )

    key = f"cards/{card.id}/{uuid4().hex}{ext}"
    await run_in_threadpool(storage.upload_bytes, key, data, file.content_type)

    return await image_crud.create(
        session, card.id, key, storage.public_url(key), is_main, color_id
    )


@router.delete(
    "/{card_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_card_image(card_id: int, image_id: int, session: SessionDep):
    image = await image_crud.get(session, image_id)
    if image is None or image.card_id != card_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found")
    await run_in_threadpool(storage.delete_object, image.key)
    await image_crud.delete(session, image)
