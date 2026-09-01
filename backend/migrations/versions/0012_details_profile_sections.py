"""Tab 4: communication channel, prior background, emotional ID sections

Revision ID: 0012_details_profile_sections
Revises: 0011_details_medical_profile
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_details_profile_sections"
down_revision: str | None = "0011_details_medical_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column(
            "expression_mode",
            sa.Enum(
                "fluent_speech",
                "words_short_sentences",
                "gestures",
                "tablet_device",
                "nonverbal",
                native_enum=False,
                length=32,
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "student_details",
        sa.Column(
            "language_comprehension",
            sa.Enum(
                "complex_instructions",
                "simple_instructions",
                native_enum=False,
                length=32,
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "student_details",
        sa.Column("current_or_last_framework", sa.String(length=300), nullable=True),
    )
    op.add_column("student_details", sa.Column("prior_task_experience", sa.Text(), nullable=True))
    op.add_column("student_details", sa.Column("interests_strengths", sa.Text(), nullable=True))
    op.add_column("student_details", sa.Column("triggers", sa.Text(), nullable=True))
    op.add_column("student_details", sa.Column("distress_early_signs", sa.Text(), nullable=True))
    op.add_column("student_details", sa.Column("calming_methods", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("student_details", "calming_methods")
    op.drop_column("student_details", "distress_early_signs")
    op.drop_column("student_details", "triggers")
    op.drop_column("student_details", "interests_strengths")
    op.drop_column("student_details", "prior_task_experience")
    op.drop_column("student_details", "current_or_last_framework")
    op.drop_column("student_details", "language_comprehension")
    op.drop_column("student_details", "expression_mode")
