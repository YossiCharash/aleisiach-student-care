"""soft-delete columns on classes

Revision ID: 0015_class_archiving
Revises: 0014_audit_auth_events
Create Date: 2026-09-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015_class_archiving"
down_revision: str | None = "0014_audit_auth_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "classes",
        sa.Column(
            "is_archived",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "classes",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("classes", sa.Column("archived_by", sa.Uuid(), nullable=True))


def downgrade() -> None:
    op.drop_column("classes", "archived_by")
    op.drop_column("classes", "archived_at")
    op.drop_column("classes", "is_archived")
