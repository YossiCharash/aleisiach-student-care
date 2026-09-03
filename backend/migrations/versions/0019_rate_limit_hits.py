"""rate limiting: a shared store so the quota survives more than one process

Revision ID: 0019_rate_limit_hits
Revises: 0018_tenant_scope_content
Create Date: 2026-09-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0019_rate_limit_hits"
down_revision: str | None = "0018_tenant_scope_content"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rate_limit_hits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bucket_key", sa.String(length=200), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_rate_limit_hits_bucket_key_occurred_at",
        "rate_limit_hits",
        ["bucket_key", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_rate_limit_hits_bucket_key_occurred_at", table_name="rate_limit_hits")
    op.drop_table("rate_limit_hits")
