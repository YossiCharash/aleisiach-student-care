"""drop the disability_severity Tab 4 field and its option category

Revision ID: 0034_drop_disability_severity
Revises: 0033_drop_current_institution
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0034_drop_disability_severity"
down_revision: str | None = "0033_drop_current_institution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text("DELETE FROM detail_options WHERE field = 'disability_severity'")
    )
    op.drop_column("student_details", "disability_severity")


def downgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column("disability_severity", sa.String(length=200), nullable=True),
    )
