"""drop the current_institution Tab 4 field

Revision ID: 0033_drop_current_institution
Revises: 0032_supported_employment
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0033_drop_current_institution"
down_revision: str | None = "0032_supported_employment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("student_details", "current_institution")


def downgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column("current_institution", sa.String(length=300), nullable=True),
    )
