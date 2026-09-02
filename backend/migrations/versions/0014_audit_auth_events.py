"""audit log: source ip + user agent, wider action column for auth events

Revision ID: 0014_audit_auth_events
Revises: 0013_detail_options_catalog
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014_audit_auth_events"
down_revision: str | None = "0013_detail_options_catalog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "audit_logs",
        "action",
        existing_type=sa.String(length=16),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
    op.add_column("audit_logs", sa.Column("ip", sa.String(length=45), nullable=True))
    op.add_column("audit_logs", sa.Column("user_agent", sa.String(length=400), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_logs", "user_agent")
    op.drop_column("audit_logs", "ip")
    op.alter_column(
        "audit_logs",
        "action",
        existing_type=sa.String(length=32),
        type_=sa.String(length=16),
        existing_nullable=False,
    )
