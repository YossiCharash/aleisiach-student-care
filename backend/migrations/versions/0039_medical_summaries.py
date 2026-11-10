"""medical information summary, one per student

Revision ID: 0039_medical_summaries
Revises: 0038_incident_reports
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0039_medical_summaries"
down_revision: str | None = "0038_incident_reports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TEXT_COLUMNS = (
    "phone",
    "allergies",
    "known_syndrome",
    "background_diseases",
    "hospitalizations_surgeries",
    "epilepsy_seizure_nature",
    "epilepsy_seizure_frequency",
    "epilepsy_seizure_treatment",
    "dual_diagnosis_expression",
    "dual_diagnosis_frequency",
    "dual_diagnosis_treatment",
    "skin_known_issues",
    "communication_other",
    "formula",
    "diet_other",
    "loves",
    "calming",
    "angering",
    "frightening",
    "stress_behavior",
    "care_recommendations",
    "general_notes",
    "guardian_name",
    "guardian_relation",
    "guardian_phone",
    "health_fund",
    "supplemental_insurance_detail",
    "attending_doctor",
    "care_nurse",
    "community_social_worker",
    "social_worker_phone",
    "filler_role",
)

_OPTION_COLUMNS = (
    "lives_with",
    "dental_treatment",
    "dentures",
    "skin_integrity",
    "comprehension",
    "communication",
    "speech",
    "vision",
    "hearing",
    "functioning",
    "mobility",
    "eating",
    "chewing_swallowing",
    "food_texture",
    "diet",
    "continence",
)

_FLAG_COLUMNS = (
    "epilepsy_known",
    "dual_diagnosis_known",
    "gastrostomy_feeding",
    "supplemental_insurance",
)


def _columns() -> list[sa.Column[object]]:
    return [
        *(sa.Column(name, sa.Text(), nullable=False) for name in _TEXT_COLUMNS),
        *(sa.Column(name, sa.JSON(), nullable=False) for name in _OPTION_COLUMNS),
        *(sa.Column(name, sa.Boolean(), nullable=True) for name in _FLAG_COLUMNS),
    ]


def upgrade() -> None:
    op.create_table(
        "medical_summaries",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        *_columns(),
        sa.Column("epilepsy_last_seizure", sa.Date(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_medical_summaries_student_institution",
        ),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index("ix_medical_summaries_institution_id", "medical_summaries", ["institution_id"])


def downgrade() -> None:
    op.drop_index("ix_medical_summaries_institution_id", table_name="medical_summaries")
    op.drop_table("medical_summaries")
