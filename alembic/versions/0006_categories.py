"""category_groups, categories (+ seed)

Revision ID: 0006_categories
Revises: 0005_lookups
Create Date: 2026-07-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_categories"
down_revision: Union[str, None] = "0005_lookups"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Стандартные группы и категории (админ дальше правит через CRUD).
SEED: dict[str, list[str]] = {
    "Верх": ["Футболки", "Лонгсливы", "Рубашки", "Свитшоты", "Худи"],
    "Низ": ["Шорты", "Брюки", "Джинсы"],
    "Верхняя одежда": ["Куртки", "Пальто"],
    "Аксессуары": ["Головные уборы", "Сумки"],
}


def upgrade() -> None:
    op.create_table(
        "category_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"], ["category_groups.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "name", name="uq_category_name"),
    )
    op.create_index("ix_categories_group_id", "categories", ["group_id"])

    conn = op.get_bind()
    for g_order, (group_name, cats) in enumerate(SEED.items(), start=1):
        conn.execute(
            sa.text(
                "INSERT INTO category_groups (name, sort_order) VALUES (:n, :o)"
            ),
            {"n": group_name, "o": g_order},
        )
        for c_order, cat_name in enumerate(cats, start=1):
            conn.execute(
                sa.text(
                    "INSERT INTO categories (group_id, name, sort_order) "
                    "SELECT id, :cn, :co FROM category_groups WHERE name = :gn"
                ),
                {"cn": cat_name, "co": c_order, "gn": group_name},
            )


def downgrade() -> None:
    op.drop_index("ix_categories_group_id", table_name="categories")
    op.drop_table("categories")
    op.drop_table("category_groups")
