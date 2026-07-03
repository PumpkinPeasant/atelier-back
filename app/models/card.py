import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class CardStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class ProductCard(Base, TimestampMixin):
    """Карточка товара для сайта. Одна на товар (1:1).

    Показывает бизнес-данные товара и его варианты (цвет × размер),
    добавляет витринные поля и статус публикации.
    """

    __tablename__ = "product_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    # Заголовок для сайта/SEO. Если пуст — используем имя товара.
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Слаг «заголовок-номер». Заполняется в crud (см. crud.card).
    slug: Mapped[str | None] = mapped_column(
        String(300), unique=True, index=True, nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Публичная цена. Если None — берётся базовая цена товара.
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[CardStatus] = mapped_column(
        Enum(CardStatus, native_enum=False, length=16),
        default=CardStatus.DRAFT,
        server_default=CardStatus.DRAFT.value,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    product: Mapped["Product"] = relationship(
        back_populates="card", lazy="selectin"
    )
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="card",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
        lazy="selectin",
    )


class ProductImage(Base, TimestampMixin):
    """Фото товара в карточке. Файл лежит в S3, здесь — ключ и публичный URL."""

    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("product_cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Опц. привязка фото к цвету — чтобы фронт переключал фото по варианту.
    color_id: Mapped[int | None] = mapped_column(
        ForeignKey("colors.id", ondelete="SET NULL"), nullable=True
    )
    key: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_main: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    card: Mapped["ProductCard"] = relationship(back_populates="images")
