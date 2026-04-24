"""create products table

Revision ID: 001
Revises:
Create Date: 2026-04-18
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "products",
            sa.column("title", sa.String),
            sa.column("price", sa.Float),
            sa.column("count", sa.Integer),
        ),
        [
            {"title": "Laptop", "price": 999.99, "count": 10},
            {"title": "Mouse", "price": 29.99, "count": 50},
        ],
    )


def downgrade() -> None:
    op.drop_table("products")
