"""student details (Tab 4 core: identity, diagnoses, contacts, guardianship)

Revision ID: 0006_student_details
Revises: 0005_team_meetings
Create Date: 2026-08-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_student_details"
down_revision: str | None = "0005_team_meetings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "student_details",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("national_id", sa.String(length=20), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("home_language", sa.String(length=100), nullable=True),
        sa.Column("medical_diagnoses", sa.JSON(), nullable=False),
        sa.Column("emergency_contacts", sa.JSON(), nullable=False),
        sa.Column("legal_status", sa.String(length=32), nullable=True),
        sa.Column("guardians", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("student_id"),
    )


def downgrade() -> None:
    op.drop_table("student_details")
