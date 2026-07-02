from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    pass


class CategoryGroup(Base, TimestampMixin):
    """Группа категорий (напр. «Верх», «Низ», «Аксессуары»)."""

    __tablename__ = "category_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    categories: Mapped[list["Category"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="Category.sort_order, Category.name",
        lazy="selectin",
    )


class Category(Base, TimestampMixin):
    """Категория товара внутри группы (напр. «Футболки»)."""

    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("group_id", "name", name="uq_category_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("category_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    group: Mapped["CategoryGroup"] = relationship(back_populates="categories")
