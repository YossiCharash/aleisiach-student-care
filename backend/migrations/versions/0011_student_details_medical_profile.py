"""Tab 4 rebuild: diagnosis catalog, IDD severity, critical medical & safety profile

Revision ID: 0011_details_medical_profile
Revises: 0010_extra_sections
Create Date: 2026-08-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_details_medical_profile"
down_revision: str | None = "0010_extra_sections"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "diagnosis_catalog",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "student_details",
        sa.Column(
            "idd_severity",
            sa.Enum("mild", "moderate", "complex", native_enum=False, length=32),
            nullable=True,
        ),
    )
    op.add_column(
        "student_details",
        sa.Column("additional_diagnoses", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "student_details",
        sa.Column(
            "has_allergies_or_dietary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "student_details",
        sa.Column("allergies_dietary", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "student_details",
        sa.Column(
            "takes_regular_medication",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "student_details",
        sa.Column("medications", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "student_details",
        sa.Column(
            "medication_independence",
            sa.Enum("not_alone", "needs_reminder", "independent", native_enum=False, length=32),
            nullable=True,
        ),
    )
    op.add_column("student_details", sa.Column("emergency_protocol", sa.Text(), nullable=True))
    op.add_column(
        "student_details",
        sa.Column("assistive_devices", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "student_details", sa.Column("assistive_device_other", sa.String(length=200), nullable=True)
    )
    op.drop_column("student_details", "medical_diagnoses")


def downgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column("medical_diagnoses", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.drop_column("student_details", "assistive_device_other")
    op.drop_column("student_details", "assistive_devices")
    op.drop_column("student_details", "emergency_protocol")
    op.drop_column("student_details", "medication_independence")
    op.drop_column("student_details", "medications")
    op.drop_column("student_details", "takes_regular_medication")
    op.drop_column("student_details", "allergies_dietary")
    op.drop_column("student_details", "has_allergies_or_dietary")
    op.drop_column("student_details", "additional_diagnoses")
    op.drop_column("student_details", "idd_severity")
    op.drop_table("diagnosis_catalog")
