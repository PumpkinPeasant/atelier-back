import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.material import Material


class ProductCategory(str, enum.Enum):
    TSHIRT = "tshirt"
    SHORTS = "shorts"
    SWEATSHIRT = "sweatshirt"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"


class Fit(str, enum.Enum):
    SLIM = "slim"
    REGULAR = "regular"
    OVERSIZE = "oversize"


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ProductCategory] = mapped_column(
        Enum(ProductCategory, native_enum=False, length=32), nullable=False
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, native_enum=False, length=16), nullable=False
    )
    fit: Mapped[Fit] = mapped_column(
        Enum(Fit, native_enum=False, length=16), nullable=False
    )
    # Плотность ткани, г/м² (GSM).
    density: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    composition: Mapped[list["ProductMaterial"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ProductMaterial(Base):
    """Состав товара: доля конкретного материала в изделии."""

    __tablename__ = "product_materials"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="RESTRICT"), primary_key=True
    )
    # Доля материала в составе, %.
    percent: Mapped[int] = mapped_column(Integer, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="composition")
    material: Mapped["Material"] = relationship(
        back_populates="products", lazy="selectin"
    )
