"""medical information summary becomes a dated, archivable series of entries

Revision ID: 0041_medical_summary_entries
Revises: 0040_risk_assessments
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0041_medical_summary_entries"
down_revision: str | None = "0040_risk_assessments"
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

_FIELD_LIST = ", ".join((*_TEXT_COLUMNS, *_OPTION_COLUMNS, *_FLAG_COLUMNS, "epilepsy_last_seizure"))
_LOCAL_DATE = "CAST(updated_at AT TIME ZONE 'Asia/Jerusalem' AS DATE)"


def _field_columns() -> list[sa.Column[object]]:
    return [
        *(sa.Column(name, sa.Text(), nullable=False) for name in _TEXT_COLUMNS),
        *(sa.Column(name, sa.JSON(), nullable=False) for name in _OPTION_COLUMNS),
        *(sa.Column(name, sa.Boolean(), nullable=True) for name in _FLAG_COLUMNS),
        sa.Column("epilepsy_last_seizure", sa.Date(), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "medical_summary_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("summary_date", sa.Date(), nullable=False),
        *_field_columns(),
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
            name="fk_medical_summary_entries_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id", "institution_id", name="uq_medical_summary_entries_id_institution"
        ),
    )
    op.create_index(
        "ix_medical_summary_entries_student_id", "medical_summary_entries", ["student_id"]
    )
    op.create_index(
        "ix_medical_summary_entries_institution_id", "medical_summary_entries", ["institution_id"]
    )
    op.execute(
        "INSERT INTO medical_summary_entries "
        f"(id, student_id, summary_date, {_FIELD_LIST}, author_id, created_at, updated_at, "
        "is_archived, institution_id) "
        f"SELECT gen_random_uuid(), student_id, {_LOCAL_DATE}, {_FIELD_LIST}, "
        "updated_by, updated_at, updated_at, false, institution_id FROM medical_summaries"
    )
    op.drop_index("ix_medical_summaries_institution_id", table_name="medical_summaries")
    op.drop_table("medical_summaries")


def downgrade() -> None:
    op.create_table(
        "medical_summaries",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        *_field_columns(),
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
    op.execute(
        "INSERT INTO medical_summaries "
        f"(student_id, {_FIELD_LIST}, updated_by, updated_at, institution_id) "
        f"SELECT DISTINCT ON (student_id) student_id, {_FIELD_LIST}, author_id, updated_at, "
        "institution_id FROM medical_summary_entries WHERE is_archived = false "
        "ORDER BY student_id, summary_date DESC, created_at DESC"
    )
    op.drop_index("ix_medical_summary_entries_institution_id", table_name="medical_summary_entries")
    op.drop_index("ix_medical_summary_entries_student_id", table_name="medical_summary_entries")
    op.drop_table("medical_summary_entries")
