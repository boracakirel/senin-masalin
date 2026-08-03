"""create stories table

Revision ID: 20260616_0001
Revises:
Create Date: 2026-06-16 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "20260616_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("child_name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("animal", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("theme", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column("favorite_color", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("baslangic", sa.Text(), nullable=False),
        sa.Column("macera", sa.Text(), nullable=False),
        sa.Column("sonuc", sa.Text(), nullable=False),
        sa.Column("moral", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stories_child_name"), "stories", ["child_name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stories_child_name"), table_name="stories")
    op.drop_table("stories")
