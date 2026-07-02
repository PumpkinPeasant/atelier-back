from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.api.deps import SessionDep
from app.core import storage
from app.crud import material as material_crud
from app.crud import product as crud
from app.crud import product_image as image_crud
from app.models.product import ProductCategory
from app.schemas.product import (
    CompositionItem,
    ProductCreate,
    ProductImageRead,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])

# Разрешённые типы изображений и максимальный размер файла.
_IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


async def _validate_composition(
    session: SessionDep, composition: list[CompositionItem]
) -> None:
    if not composition:
        return

    material_ids = [item.material_id for item in composition]
    if len(material_ids) != len(set(material_ids)):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Duplicate material in composition"
        )

    existing = await material_crud.existing_ids(session, material_ids)
    missing = sorted(set(material_ids) - existing)
    if missing:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Materials not found: {missing}"
        )

    total = sum(item.percent for item in composition)
    if total != 100:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Composition percentages must sum to 100, got {total}",
        )


@router.get("", response_model=list[ProductRead])
async def list_products(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    category: ProductCategory | None = None,
):
    return await crud.list_(session, skip=skip, limit=limit, category=category)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, session: SessionDep):
    await _validate_composition(session, payload.composition)
    return await crud.create(session, payload)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: SessionDep):
    product = await crud.get(session, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int, payload: ProductUpdate, session: SessionDep
):
    product = await crud.get(session, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    if payload.composition is not None:
        await _validate_composition(session, payload.composition)
    return await crud.update(session, product, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: SessionDep):
    product = await crud.get(session, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    # Удаляем файлы из S3 до удаления товара (в БД строки уйдут по каскаду).
    for image in product.images:
        await run_in_threadpool(storage.delete_object, image.key)
    await crud.delete(session, product)


@router.post(
    "/{product_id}/images",
    response_model=ProductImageRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_image(
    product_id: int,
    session: SessionDep,
    file: UploadFile = File(...),
    is_main: bool = Form(False),
):
    product = await crud.get(session, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

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

    key = f"products/{product_id}/{uuid4().hex}{ext}"
    await run_in_threadpool(storage.upload_bytes, key, data, file.content_type)

    return await image_crud.create(
        session, product_id, key, storage.public_url(key), is_main
    )


@router.delete(
    "/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product_image(product_id: int, image_id: int, session: SessionDep):
    image = await image_crud.get(session, image_id)
    if image is None or image.product_id != product_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found")
    await run_in_threadpool(storage.delete_object, image.key)
    await image_crud.delete(session, image)
