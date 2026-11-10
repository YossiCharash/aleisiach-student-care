"""incident reports (Form 35): a dated, archivable series per student

Revision ID: 0038_incident_reports
Revises: 0037_functional_report_entries
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0038_incident_reports"
down_revision: str | None = "0037_functional_report_entries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TEXT_COLUMNS = (
    "location",
    "reporter_name_role",
    "nature_other",
    "description",
    "staff_present",
    "affected_service_recipients",
    "warning_signs",
    "actions_taken",
    "referral_other",
    "decision_reasons",
    "incident_causes",
    "was_preventable",
    "lessons_learned",
    "corrective_action_plan",
    "filler_name",
    "filler_role",
)


def _text_columns() -> list[sa.Column[str]]:
    return [sa.Column(name, sa.Text(), nullable=False) for name in _TEXT_COLUMNS]


def upgrade() -> None:
    op.create_table(
        "incident_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("event_time", sa.Time(), nullable=True),
        sa.Column("report_type", sa.String(length=16), nullable=True),
        sa.Column("natures", sa.JSON(), nullable=False),
        sa.Column("referrals", sa.JSON(), nullable=False),
        sa.Column("manager_updated_date", sa.Date(), nullable=True),
        sa.Column("manager_updated_time", sa.Time(), nullable=True),
        *_text_columns(),
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
            name="fk_incident_reports_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_incident_reports_id_institution"),
    )
    op.create_index("ix_incident_reports_student_id", "incident_reports", ["student_id"])
    op.create_index("ix_incident_reports_institution_id", "incident_reports", ["institution_id"])


def downgrade() -> None:
    op.drop_index("ix_incident_reports_institution_id", table_name="incident_reports")
    op.drop_index("ix_incident_reports_student_id", table_name="incident_reports")
    op.drop_table("incident_reports")
