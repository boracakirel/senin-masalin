"""rename story theme to themes

Revision ID: 20260723_0002
Revises: 20260616_0001
Create Date: 2026-07-23 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "20260723_0002"
down_revision: str | None = "20260616_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "stories",
        "theme",
        new_column_name="themes",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=200),
        type_=sa.String(length=500),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "stories",
        "themes",
        new_column_name="theme",
        existing_type=sa.String(length=500),
        type_=sqlmodel.sql.sqltypes.AutoString(length=200),
        existing_nullable=False,
    )
