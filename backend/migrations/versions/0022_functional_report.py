"""functional report (Tab 5), one per student

Revision ID: 0022_functional_report
Revises: 0021_manual_program
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022_functional_report"
down_revision: str | None = "0021_manual_program"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "functional_reports",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("general_background", sa.Text(), nullable=False),
        sa.Column("vocational_domain", sa.Text(), nullable=False),
        sa.Column("behavioral_emotional_domain", sa.Text(), nullable=False),
        sa.Column("communication_social_domain", sa.Text(), nullable=False),
        sa.Column("independence_life_skills_domain", sa.Text(), nullable=False),
        sa.Column("summary_recommendations", sa.Text(), nullable=False),
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
        "ix_functional_reports_institution_id",
        "functional_reports",
        ["institution_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_functional_reports_institution_id", table_name="functional_reports")
    op.drop_table("functional_reports")
