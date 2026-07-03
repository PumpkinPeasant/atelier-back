from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.card import CardStatus
from app.schemas.product import ProductRead


class ProductImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    color_id: int | None = None
    sort_order: int
    is_main: bool


class ProductCardBase(BaseModel):
    title: str | None = None
    description: str | None = None
    # Публичная цена. Если None — на сайте используется базовая цена товара.
    price: Decimal | None = Field(default=None, ge=0)


class ProductCardCreate(ProductCardBase):
    product_id: int


class ProductCardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None


class ProductCardRead(ProductCardBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    slug: str | None = None
    status: CardStatus
    published_at: datetime | None = None
    images: list[ProductImageRead] = Field(default_factory=list)
    product: ProductRead
