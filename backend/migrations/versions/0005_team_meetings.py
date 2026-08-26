"""team meetings, entries, and chosen solutions (Tab 2)

Revision ID: 0005_team_meetings
Revises: 0004_taxonomy
Create Date: 2026-08-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_team_meetings"
down_revision: str | None = "0004_taxonomy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "team_meetings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_team_meetings_student_id", "team_meetings", ["student_id"])
    op.create_table(
        "meeting_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meeting_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("skill_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["team_meetings.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meeting_entries_meeting_id", "meeting_entries", ["meeting_id"])
    op.create_table(
        "meeting_entry_solutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meeting_entry_id", sa.Uuid(), nullable=False),
        sa.Column("solution_id", sa.Uuid(), nullable=False),
        sa.Column("solution_text_snapshot", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["meeting_entry_id"], ["meeting_entries.id"]),
        sa.ForeignKeyConstraint(["solution_id"], ["solutions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meeting_entry_solutions_meeting_entry_id",
        "meeting_entry_solutions",
        ["meeting_entry_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_meeting_entry_solutions_meeting_entry_id", table_name="meeting_entry_solutions"
    )
    op.drop_table("meeting_entry_solutions")
    op.drop_index("ix_meeting_entries_meeting_id", table_name="meeting_entries")
    op.drop_table("meeting_entries")
    op.drop_index("ix_team_meetings_student_id", table_name="team_meetings")
    op.drop_table("team_meetings")
