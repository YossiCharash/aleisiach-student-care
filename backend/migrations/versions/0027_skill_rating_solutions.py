"""per-skill rating descriptions and rating-scoped solutions (Tab 1)

Revision ID: 0027_skill_rating_solutions
Revises: 0026_workshops
Create Date: 2026-09-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0027_skill_rating_solutions"
down_revision: str | None = "0026_workshops"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_RATING_TEXT_COLUMNS = ("green_text", "yellow_text", "red_text")


def upgrade() -> None:
    for column in _RATING_TEXT_COLUMNS:
        op.add_column(
            "skills",
            sa.Column(column, sa.String(length=500), nullable=False, server_default=""),
        )
        op.alter_column("skills", column, server_default=None)

    op.add_column(
        "solutions",
        sa.Column("rating", sa.String(length=16), nullable=False, server_default="yellow"),
    )
    op.alter_column("solutions", "rating", server_default=None)


def downgrade() -> None:
    op.drop_column("solutions", "rating")
    for column in reversed(_RATING_TEXT_COLUMNS):
        op.drop_column("skills", column)
