"""products.slug

Revision ID: 0007_product_slug
Revises: 0006_categories
Create Date: 2026-07-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.slug import make_slug

revision: str = "0007_product_slug"
down_revision: Union[str, None] = "0006_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("slug", sa.String(length=300), nullable=True))

    # Бэкфилл слагов для уже существующих товаров.
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, name FROM products")).fetchall()
    for row in rows:
        conn.execute(
            sa.text("UPDATE products SET slug = :slug WHERE id = :id"),
            {"slug": make_slug(row.name, row.id), "id": row.id},
        )

    op.create_index("ix_products_slug", "products", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_column("products", "slug")
