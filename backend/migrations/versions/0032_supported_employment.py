"""supported employment analysis (Form 46), one per student

Revision ID: 0032_supported_employment
Revises: 0031_reception_report
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0032_supported_employment"
down_revision: str | None = "0031_reception_report"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "supported_employments",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("workplace", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("activity_type", sa.Text(), nullable=False),
        sa.Column("work_process", sa.Text(), nullable=False),
        sa.Column("work_environment", sa.Text(), nullable=False),
        sa.Column("required_body_functions", sa.Text(), nullable=False),
        sa.Column("hazards_and_safety", sa.Text(), nullable=False),
        sa.Column("workplace_contact", sa.Text(), nullable=False),
        sa.Column("escort_contact", sa.Text(), nullable=False),
        sa.Column("mobility", sa.Text(), nullable=False),
        sa.Column("work_hours", sa.Text(), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_supported_employments_student_institution",
        ),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index(
        "ix_supported_employments_institution_id",
        "supported_employments",
        ["institution_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_supported_employments_institution_id", table_name="supported_employments")
    op.drop_table("supported_employments")
