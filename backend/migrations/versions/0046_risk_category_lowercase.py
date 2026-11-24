"""risk domains: lowercase every category again, for databases that were downgraded past 0043
and moved back to head without re-running it

Revision ID: 0046_risk_category_lowercase
Revises: 0045_student_phone
Create Date: 2026-11-24
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0046_risk_category_lowercase"
down_revision: str | None = "0045_student_phone"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE risk_domains SET category = LOWER(category) WHERE category <> LOWER(category)"
    )


def downgrade() -> None:
    pass
