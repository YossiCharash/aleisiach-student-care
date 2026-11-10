"""risk assessments: a dated, archivable series of risk-management tables per student

Revision ID: 0040_risk_assessments
Revises: 0039_medical_summaries
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0040_risk_assessments"
down_revision: str | None = "0039_medical_summaries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("assessment_date", sa.Date(), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
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
            name="fk_risk_assessments_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_risk_assessments_id_institution"),
    )
    op.create_index("ix_risk_assessments_student_id", "risk_assessments", ["student_id"])
    op.create_index("ix_risk_assessments_institution_id", "risk_assessments", ["institution_id"])


def downgrade() -> None:
    op.drop_index("ix_risk_assessments_institution_id", table_name="risk_assessments")
    op.drop_index("ix_risk_assessments_student_id", table_name="risk_assessments")
    op.drop_table("risk_assessments")
