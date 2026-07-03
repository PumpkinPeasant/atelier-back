from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import card as crud
from app.models.card import CardStatus, ProductCard
from app.schemas.card import ProductCardRead

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _ensure_published(card: ProductCard | None) -> ProductCard:
    if card is None or card.status != CardStatus.PUBLISHED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return card


@router.get("/products", response_model=list[ProductCardRead])
async def list_catalog(session: SessionDep, skip: int = 0, limit: int = 100):
    """Каталог (витрина): только опубликованные карточки."""
    return await crud.list_(
        session, skip=skip, limit=limit, status=CardStatus.PUBLISHED
    )


@router.get("/products/by-slug/{slug}", response_model=ProductCardRead)
async def get_catalog_product_by_slug(slug: str, session: SessionDep):
    """Карточка товара по слагу."""
    return _ensure_published(await crud.get_by_slug(session, slug))


@router.get("/products/{card_id}", response_model=ProductCardRead)
async def get_catalog_product(card_id: int, session: SessionDep):
    """Карточка товара по id."""
    return _ensure_published(await crud.get(session, card_id))
