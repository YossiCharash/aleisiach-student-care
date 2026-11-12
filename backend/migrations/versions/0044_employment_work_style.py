"""supported employment: work style (individual / group)

Revision ID: 0044_employment_work_style
Revises: 0043_risk_category_values
Create Date: 2026-11-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0044_employment_work_style"
down_revision: str | None = "0043_risk_category_values"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "supported_employments",
        sa.Column("work_style", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("supported_employments", "work_style")
