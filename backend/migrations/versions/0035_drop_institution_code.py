"""drop the institution code field

Revision ID: 0035_drop_institution_code
Revises: 0034_drop_disability_severity
Create Date: 2026-09-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0035_drop_institution_code"
down_revision: str | None = "0034_drop_disability_severity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("institutions", "code")


def downgrade() -> None:
    op.add_column(
        "institutions",
        sa.Column("code", sa.String(length=40), nullable=True),
    )
