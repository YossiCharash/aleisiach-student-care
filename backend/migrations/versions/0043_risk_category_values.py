"""risk domains: store every category by its value ('medical'), as the seed in 0040 does

Revision ID: 0043_risk_category_values
Revises: 0042_health_records
Create Date: 2026-11-10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0043_risk_category_values"
down_revision: str | None = "0042_health_records"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE risk_domains SET category = LOWER(category) WHERE category <> LOWER(category)"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE risk_domains SET category = UPPER(category) WHERE category <> UPPER(category)"
    )
