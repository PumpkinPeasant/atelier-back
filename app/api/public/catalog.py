from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import product as crud
from app.models.product import ProductCategory
from app.schemas.product import ProductRead

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/products", response_model=list[ProductRead])
async def list_catalog(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    category: ProductCategory | None = None,
):
    """Каталог товаров (витрина)."""
    return await crud.list_(session, skip=skip, limit=limit, category=category)


@router.get("/products/by-slug/{slug}", response_model=ProductRead)
async def get_catalog_product_by_slug(slug: str, session: SessionDep):
    """Карточка товара по слагу."""
    product = await crud.get_by_slug(session, slug)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_catalog_product(product_id: int, session: SessionDep):
    """Карточка товара."""
    product = await crud.get(session, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product
