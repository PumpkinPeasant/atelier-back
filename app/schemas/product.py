from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.card import CardStatus
from app.models.product import Fit, Gender, ProductCategory
from app.schemas.lookup import ColorRead, SizeRead
from app.schemas.material import MaterialRead


class CompositionItem(BaseModel):
    """Материал в составе товара с долей в процентах."""

    material_id: int
    percent: int = Field(gt=0, le=100, description="Доля материала, %")


class CompositionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    percent: int
    material: MaterialRead


class VariantItem(BaseModel):
    """Вариант (SKU) при создании/обновлении товара."""

    color_id: int
    size_id: int
    sku: str | None = None
    stock: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0)


class VariantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    color_id: int
    size_id: int
    sku: str | None = None
    stock: int | None = None
    price: Decimal | None = None
    color: ColorRead
    size: SizeRead


class CardBrief(BaseModel):
    """Краткая инфа о карточке товара для админ-списка."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str | None = None
    title: str | None = None
    status: CardStatus
    published_at: datetime | None = None


class ProductBase(BaseModel):
    name: str
    category: ProductCategory
    gender: Gender
    fit: Fit
    density: int = Field(gt=0, description="Плотность ткани, г/м²")
    price: Decimal = Decimal("0")


class ProductCreate(ProductBase):
    composition: list[CompositionItem] = Field(default_factory=list)
    variants: list[VariantItem] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = None
    category: ProductCategory | None = None
    gender: Gender | None = None
    fit: Fit | None = None
    density: int | None = Field(default=None, gt=0)
    price: Decimal | None = None
    # Если передан — полностью заменяет текущий состав.
    composition: list[CompositionItem] | None = None
    # Если передан — полностью заменяет текущий набор вариантов.
    variants: list[VariantItem] | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    composition: list[CompositionRead] = Field(default_factory=list)
    variants: list[VariantRead] = Field(default_factory=list)
    card: CardBrief | None = None
