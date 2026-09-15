"""reception report (Form 39), one per student

Revision ID: 0031_reception_report
Revises: 0030_social_note_entries
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0031_reception_report"
down_revision: str | None = "0030_social_note_entries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reception_reports",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("committee_date", sa.Date(), nullable=True),
        sa.Column("committee_participants", sa.Text(), nullable=False),
        sa.Column("intake_date", sa.Date(), nullable=True),
        sa.Column("committee_summary", sa.Text(), nullable=False),
        sa.Column("committee_recommendations", sa.Text(), nullable=False),
        sa.Column("framework_code", sa.String(length=100), nullable=False),
        sa.Column("tariff_code", sa.String(length=100), nullable=False),
        sa.Column("committee_held", sa.Boolean(), nullable=False),
        sa.Column("committee_held_note", sa.Text(), nullable=False),
        sa.Column("director_approval", sa.Boolean(), nullable=False),
        sa.Column("director_approval_note", sa.Text(), nullable=False),
        sa.Column("family_guardian_housing_updated", sa.Boolean(), nullable=False),
        sa.Column("family_guardian_housing_updated_note", sa.Text(), nullable=False),
        sa.Column("community_social_worker_updated", sa.Boolean(), nullable=False),
        sa.Column("community_social_worker_updated_note", sa.Text(), nullable=False),
        sa.Column("management_updated", sa.Boolean(), nullable=False),
        sa.Column("management_updated_note", sa.Text(), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_reception_reports_student_institution",
        ),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index(
        "ix_reception_reports_institution_id",
        "reception_reports",
        ["institution_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_reception_reports_institution_id", table_name="reception_reports")
    op.drop_table("reception_reports")
