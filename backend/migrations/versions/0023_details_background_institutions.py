"""consolidate Tab 4 background fields to previous/current institution

Revision ID: 0023_details_background_institutions
Revises: 0022_functional_report
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0023_details_background_institutions"
down_revision: str | None = "0022_functional_report"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "student_details", "last_study_framework", new_column_name="previous_institution"
    )
    op.alter_column("student_details", "current_framework", new_column_name="current_institution")
    op.drop_column("student_details", "current_or_last_framework")


def downgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column("current_or_last_framework", sa.String(length=300), nullable=True),
    )
    op.alter_column("student_details", "current_institution", new_column_name="current_framework")
    op.alter_column(
        "student_details", "previous_institution", new_column_name="last_study_framework"
    )
