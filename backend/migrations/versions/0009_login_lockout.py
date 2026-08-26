"""login lockout + reset throttle columns on users

Revision ID: 0009_login_lockout
Revises: 0008_social_notes
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_login_lockout"
down_revision: str | None = "0008_social_notes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "failed_login_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("last_reset_request_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "last_reset_request_at")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_count")
