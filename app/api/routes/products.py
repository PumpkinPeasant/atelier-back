from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import material as material_crud
from app.crud import product as crud
from app.models.product import ProductCategory
from app.schemas.product import (
    CompositionItem,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])


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
    await crud.delete(session, product)
