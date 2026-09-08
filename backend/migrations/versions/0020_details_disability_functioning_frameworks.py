"""Tab 4: disability description, functioning level, split study frameworks

Revision ID: 0020_details_disability_functioning_frameworks
Revises: 0019_rate_limit_hits
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020_details_disability_functioning_frameworks"
down_revision: str | None = "0019_rate_limit_hits"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column("disability_severity", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "student_details",
        sa.Column("functioning_level", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "student_details",
        sa.Column("last_study_framework", sa.String(length=300), nullable=True),
    )
    op.add_column(
        "student_details",
        sa.Column("current_framework", sa.String(length=300), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("student_details", "current_framework")
    op.drop_column("student_details", "last_study_framework")
    op.drop_column("student_details", "functioning_level")
    op.drop_column("student_details", "disability_severity")
