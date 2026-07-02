from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import Fit, Gender, ProductCategory
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


class ProductImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    sort_order: int
    is_main: bool


class ProductBase(BaseModel):
    name: str
    category: ProductCategory
    gender: Gender
    fit: Fit
    density: int = Field(gt=0, description="Плотность ткани, г/м²")
    description: str | None = None
    price: Decimal = Decimal("0")


class ProductCreate(ProductBase):
    composition: list[CompositionItem] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = None
    category: ProductCategory | None = None
    gender: Gender | None = None
    fit: Fit | None = None
    density: int | None = Field(default=None, gt=0)
    description: str | None = None
    price: Decimal | None = None
    # Если передан — полностью заменяет текущий состав.
    composition: list[CompositionItem] | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    composition: list[CompositionRead] = Field(default_factory=list)
    images: list[ProductImageRead] = Field(default_factory=list)
