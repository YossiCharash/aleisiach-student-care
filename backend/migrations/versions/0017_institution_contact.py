"""institutions: contact person and phone

Revision ID: 0017_institution_contact
Revises: 0016_institutions
Create Date: 2026-09-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017_institution_contact"
down_revision: str | None = "0016_institutions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("institutions", sa.Column("contact_name", sa.String(length=200), nullable=True))
    op.add_column("institutions", sa.Column("contact_phone", sa.String(length=40), nullable=True))


def downgrade() -> None:
    op.drop_column("institutions", "contact_phone")
    op.drop_column("institutions", "contact_name")
