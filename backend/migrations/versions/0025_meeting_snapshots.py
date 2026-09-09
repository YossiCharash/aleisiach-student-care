"""team meetings snapshot foci + plan with a dated summary (Tab 2)

Revision ID: 0025_meeting_snapshots
Revises: 0024_program_plans
Create Date: 2026-09-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0025_meeting_snapshots"
down_revision: str | None = "0024_program_plans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("meeting_entry_solutions")
    op.drop_table("meeting_entries")
    op.drop_table("team_meetings")

    op.create_table(
        "team_meetings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("meeting_date", sa.Date(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_team_meetings_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_team_meetings_id_institution"),
    )
    op.create_index("ix_team_meetings_student_id", "team_meetings", ["student_id"])
    op.create_index("ix_team_meetings_institution_id", "team_meetings", ["institution_id"])

    _create_snapshot_entries("meeting_foci_entries")
    _create_snapshot_entries("meeting_plan_entries")

    op.create_table(
        "meeting_plan_solutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_entry_id", sa.Uuid(), nullable=False),
        sa.Column("solution_id", sa.Uuid(), nullable=False),
        sa.Column("solution_text_snapshot", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["plan_entry_id", "institution_id"],
            ["meeting_plan_entries.id", "meeting_plan_entries.institution_id"],
            name="fk_meeting_plan_solutions_entry_institution",
        ),
        sa.ForeignKeyConstraint(
            ["solution_id", "institution_id"],
            ["solutions.id", "solutions.institution_id"],
            name="fk_meeting_plan_solutions_solution_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meeting_plan_solutions_plan_entry_id",
        "meeting_plan_solutions",
        ["plan_entry_id"],
    )
    op.create_index(
        "ix_meeting_plan_solutions_institution_id",
        "meeting_plan_solutions",
        ["institution_id"],
    )


def _create_snapshot_entries(table_name: str) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meeting_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("skill_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["meeting_id", "institution_id"],
            ["team_meetings.id", "team_meetings.institution_id"],
            name=f"fk_{table_name}_meeting_institution",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name=f"fk_{table_name}_skill_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name=f"uq_{table_name}_id_institution"),
    )
    op.create_index(f"ix_{table_name}_meeting_id", table_name, ["meeting_id"])
    op.create_index(f"ix_{table_name}_institution_id", table_name, ["institution_id"])


def downgrade() -> None:
    op.drop_table("meeting_plan_solutions")
    op.drop_table("meeting_plan_entries")
    op.drop_table("meeting_foci_entries")
    op.drop_table("team_meetings")

    op.create_table(
        "team_meetings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_team_meetings_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_team_meetings_id_institution"),
    )
    op.create_index("ix_team_meetings_student_id", "team_meetings", ["student_id"])
    op.create_index("ix_team_meetings_institution_id", "team_meetings", ["institution_id"])

    op.create_table(
        "meeting_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meeting_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("skill_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["meeting_id", "institution_id"],
            ["team_meetings.id", "team_meetings.institution_id"],
            name="fk_meeting_entries_meeting_institution",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_meeting_entries_skill_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_meeting_entries_id_institution"),
    )
    op.create_index("ix_meeting_entries_meeting_id", "meeting_entries", ["meeting_id"])
    op.create_index("ix_meeting_entries_institution_id", "meeting_entries", ["institution_id"])

    op.create_table(
        "meeting_entry_solutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meeting_entry_id", sa.Uuid(), nullable=False),
        sa.Column("solution_id", sa.Uuid(), nullable=False),
        sa.Column("solution_text_snapshot", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["meeting_entry_id", "institution_id"],
            ["meeting_entries.id", "meeting_entries.institution_id"],
            name="fk_meeting_entry_solutions_entry_institution",
        ),
        sa.ForeignKeyConstraint(
            ["solution_id", "institution_id"],
            ["solutions.id", "solutions.institution_id"],
            name="fk_meeting_entry_solutions_solution_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meeting_entry_solutions_meeting_entry_id",
        "meeting_entry_solutions",
        ["meeting_entry_id"],
    )
    op.create_index(
        "ix_meeting_entry_solutions_institution_id",
        "meeting_entry_solutions",
        ["institution_id"],
    )
