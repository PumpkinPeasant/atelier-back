"""product cards and variants; move images to cards

Revision ID: 0008_cards_and_variants
Revises: 0007_product_slug
Create Date: 2026-07-03

Расщепляем товар: `products` остаётся справочником (бизнес-данные), витрина
переезжает в `product_cards` (1:1), а конкретные SKU — в `product_variants`
(цвет × размер). Фото перевешиваются с товара на карточку.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_cards_and_variants"
down_revision: Union[str, None] = "0007_product_slug"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Варианты (SKU): цвет × размер.
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("color_id", sa.Integer(), nullable=False),
        sa.Column("size_id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["color_id"], ["colors.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["size_id"], ["sizes.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "color_id", "size_id", name="uq_variant"),
    )
    op.create_index(
        "ix_product_variants_product_id", "product_variants", ["product_id"]
    )

    # 2. Карточки товара (1:1 с товаром).
    op.create_table(
        "product_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="draft", nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", name="uq_card_product"),
    )
    op.create_index("ix_product_cards_product_id", "product_cards", ["product_id"])
    op.create_index("ix_product_cards_slug", "product_cards", ["slug"], unique=True)

    # 3. Бэкфилл: карточка на каждый существующий товар (переносим slug/описание).
    #    Статус — published, чтобы витрина не опустела.
    products = conn.execute(
        sa.text("SELECT id, slug, description FROM products")
    ).fetchall()
    for p in products:
        conn.execute(
            sa.text(
                "INSERT INTO product_cards "
                "(product_id, slug, description, status, published_at, "
                "created_at, updated_at) "
                "VALUES (:pid, :slug, :descr, 'published', now(), now(), now())"
            ),
            {"pid": p.id, "slug": p.slug, "descr": p.description},
        )

    # 4. product_images: переезд с product_id на card_id (+ опц. color_id).
    op.add_column("product_images", sa.Column("card_id", sa.Integer(), nullable=True))
    op.add_column("product_images", sa.Column("color_id", sa.Integer(), nullable=True))
    conn.execute(
        sa.text(
            "UPDATE product_images pi SET card_id = pc.id "
            "FROM product_cards pc WHERE pc.product_id = pi.product_id"
        )
    )
    # Осиротевшие фото без карточки (не ожидаются) — убираем.
    conn.execute(sa.text("DELETE FROM product_images WHERE card_id IS NULL"))

    op.execute(
        "ALTER TABLE product_images "
        "DROP CONSTRAINT IF EXISTS product_images_product_id_fkey"
    )
    op.drop_index("ix_product_images_product_id", table_name="product_images")
    op.drop_column("product_images", "product_id")

    op.alter_column("product_images", "card_id", nullable=False)
    op.create_index("ix_product_images_card_id", "product_images", ["card_id"])
    op.create_foreign_key(
        "fk_product_images_card_id",
        "product_images",
        "product_cards",
        ["card_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_product_images_color_id",
        "product_images",
        "colors",
        ["color_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 5. products: slug и description переехали в карточку.
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_column("products", "slug")
    op.drop_column("products", "description")


def downgrade() -> None:
    conn = op.get_bind()

    # products: возвращаем slug/description из карточек.
    op.add_column("products", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("slug", sa.String(length=300), nullable=True))
    conn.execute(
        sa.text(
            "UPDATE products p SET slug = pc.slug, description = pc.description "
            "FROM product_cards pc WHERE pc.product_id = p.id"
        )
    )
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)

    # product_images: возвращаем product_id.
    op.add_column(
        "product_images", sa.Column("product_id", sa.Integer(), nullable=True)
    )
    conn.execute(
        sa.text(
            "UPDATE product_images pi SET product_id = pc.product_id "
            "FROM product_cards pc WHERE pc.id = pi.card_id"
        )
    )
    op.execute(
        "ALTER TABLE product_images "
        "DROP CONSTRAINT IF EXISTS fk_product_images_card_id"
    )
    op.execute(
        "ALTER TABLE product_images "
        "DROP CONSTRAINT IF EXISTS fk_product_images_color_id"
    )
    op.drop_index("ix_product_images_card_id", table_name="product_images")
    op.drop_column("product_images", "color_id")
    op.drop_column("product_images", "card_id")
    op.alter_column("product_images", "product_id", nullable=False)
    op.create_index(
        "ix_product_images_product_id", "product_images", ["product_id"]
    )
    op.create_foreign_key(
        "product_images_product_id_fkey",
        "product_images",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_index("ix_product_cards_slug", table_name="product_cards")
    op.drop_index("ix_product_cards_product_id", table_name="product_cards")
    op.drop_table("product_cards")

    op.drop_index(
        "ix_product_variants_product_id", table_name="product_variants"
    )
    op.drop_table("product_variants")
