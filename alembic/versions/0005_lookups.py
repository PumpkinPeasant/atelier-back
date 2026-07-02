"""lookups: colors, sizes (+ seed)

Revision ID: 0005_lookups
Revises: 0004_product_images
Create Date: 2026-07-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_lookups"
down_revision: Union[str, None] = "0004_product_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    colors = op.create_table(
        "colors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("hex", sa.String(length=7), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    sizes = op.create_table(
        "sizes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.bulk_insert(
        colors,
        [
            {"name": "Чёрный", "hex": "#000000"},
            {"name": "Белый", "hex": "#FFFFFF"},
            {"name": "Серый", "hex": "#808080"},
            {"name": "Синий", "hex": "#0000FF"},
            {"name": "Красный", "hex": "#FF0000"},
            {"name": "Зелёный", "hex": "#008000"},
            {"name": "Бежевый", "hex": "#F5F5DC"},
        ],
    )
    op.bulk_insert(
        sizes,
        [
            {"name": "XS", "sort_order": 1},
            {"name": "S", "sort_order": 2},
            {"name": "M", "sort_order": 3},
            {"name": "L", "sort_order": 4},
            {"name": "XL", "sort_order": 5},
            {"name": "XXL", "sort_order": 6},
        ],
    )


def downgrade() -> None:
    op.drop_table("sizes")
    op.drop_table("colors")
