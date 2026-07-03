import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.card import ProductCard
    from app.models.color import Color
    from app.models.material import Material
    from app.models.size import Size


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
    """Товар-справочник: родительская бизнес-сущность (напр. «Футболка»).

    Витрина (slug, описание, фото, статус публикации) вынесена в ProductCard,
    конкретные SKU (цвет × размер) — в ProductVariant.
    """

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
    # Базовая (бизнес) цена. Публичную цену может переопределить карточка/вариант.
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    composition: Mapped[list["ProductMaterial"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductVariant.id",
        lazy="selectin",
    )
    card: Mapped["ProductCard | None"] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        uselist=False,
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


class ProductVariant(Base, TimestampMixin):
    """Вариант товара (SKU): конкретное сочетание цвета и размера."""

    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "color_id", "size_id", name="uq_variant"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    color_id: Mapped[int] = mapped_column(
        ForeignKey("colors.id", ondelete="RESTRICT"), nullable=False
    )
    size_id: Mapped[int] = mapped_column(
        ForeignKey("sizes.id", ondelete="RESTRICT"), nullable=False
    )
    # Артикул конкретного SKU (опц.).
    sku: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Остаток на складе (опц., None = не отслеживается).
    stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Переопределение цены для конкретного SKU (опц.).
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    product: Mapped["Product"] = relationship(back_populates="variants")
    color: Mapped["Color"] = relationship(lazy="selectin")
    size: Mapped["Size"] = relationship(lazy="selectin")
