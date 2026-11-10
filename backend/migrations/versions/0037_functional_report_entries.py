"""functional report (Tab 5) becomes a dated, archivable series of entries

Revision ID: 0037_functional_report_entries
Revises: 0036_meeting_participants
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0037_functional_report_entries"
down_revision: str | None = "0036_meeting_participants"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SECTIONS = (
    "general_background",
    "vocational_domain",
    "behavioral_emotional_domain",
    "communication_social_domain",
    "independence_life_skills_domain",
    "summary_recommendations",
)
_SECTION_LIST = ", ".join(_SECTIONS)
_LOCAL_DATE = "CAST(updated_at AT TIME ZONE 'Asia/Jerusalem' AS DATE)"


def _section_columns() -> list[sa.Column[str]]:
    return [sa.Column(name, sa.Text(), nullable=False) for name in _SECTIONS]


def upgrade() -> None:
    op.create_table(
        "functional_report_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("report_date", sa.Date(), nullable=False),
        *_section_columns(),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.Uuid(), nullable=True),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_functional_report_entries_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "institution_id", name="uq_functional_report_entries_id_institution"
        ),
    )
    op.create_index(
        "ix_functional_report_entries_student_id", "functional_report_entries", ["student_id"]
    )
    op.create_index(
        "ix_functional_report_entries_institution_id",
        "functional_report_entries",
        ["institution_id"],
    )
    op.execute(
        "INSERT INTO functional_report_entries "
        f"(id, student_id, report_date, {_SECTION_LIST}, author_id, created_at, updated_at, "
        "is_archived, institution_id) "
        f"SELECT gen_random_uuid(), student_id, {_LOCAL_DATE}, {_SECTION_LIST}, "
        "updated_by, updated_at, updated_at, false, institution_id FROM functional_reports"
    )
    op.drop_index("ix_functional_reports_institution_id", table_name="functional_reports")
    op.drop_table("functional_reports")


def downgrade() -> None:
    op.create_table(
        "functional_reports",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        *_section_columns(),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_functional_reports_student_institution",
        ),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index(
        "ix_functional_reports_institution_id", "functional_reports", ["institution_id"]
    )
    op.execute(
        "INSERT INTO functional_reports "
        f"(student_id, {_SECTION_LIST}, updated_by, updated_at, institution_id) "
        f"SELECT DISTINCT ON (student_id) student_id, {_SECTION_LIST}, author_id, updated_at, "
        "institution_id FROM functional_report_entries WHERE is_archived = false "
        "ORDER BY student_id, report_date DESC, created_at DESC"
    )
    op.drop_index(
        "ix_functional_report_entries_institution_id", table_name="functional_report_entries"
    )
    op.drop_index("ix_functional_report_entries_student_id", table_name="functional_report_entries")
    op.drop_table("functional_report_entries")
