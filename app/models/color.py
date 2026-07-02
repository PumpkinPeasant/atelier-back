from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Color(Base, TimestampMixin):
    __tablename__ = "colors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # HEX для превью-свотча в UI, напр. "#000000".
    hex: Mapped[str | None] = mapped_column(String(7), nullable=True)
