"""add participants to team meetings

Revision ID: 0036_meeting_participants
Revises: 0035_drop_institution_code
Create Date: 2026-09-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0036_meeting_participants"
down_revision: str | None = "0035_drop_institution_code"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "team_meetings",
        sa.Column("participants", sa.Text(), nullable=False, server_default=""),
    )
    op.alter_column("team_meetings", "participants", server_default=None)


def downgrade() -> None:
    op.drop_column("team_meetings", "participants")
