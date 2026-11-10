"""health-professions documentation: institution health domains + per-student documentation rows

Revision ID: 0042_health_records
Revises: 0041_medical_summary_entries
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0042_health_records"
down_revision: str | None = "0041_medical_summary_entries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _create_health_domains() -> None:
    op.create_table(
        "health_domains",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_health_domains_id_institution"),
    )
    op.create_index("ix_health_domains_institution_id", "health_domains", ["institution_id"])


def _create_health_records() -> None:
    op.create_table(
        "health_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("domain_id", sa.Uuid(), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("session_type", sa.String(length=16), nullable=True),
        sa.Column("support_given", sa.Text(), nullable=False),
        sa.Column("responsible_user_ids", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("execution_review", sa.Text(), nullable=False),
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
            name="fk_health_records_student_institution",
        ),
        sa.ForeignKeyConstraint(
            ["domain_id", "institution_id"],
            ["health_domains.id", "health_domains.institution_id"],
            name="fk_health_records_domain_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_health_records_id_institution"),
    )
    op.create_index("ix_health_records_student_id", "health_records", ["student_id"])
    op.create_index("ix_health_records_domain_id", "health_records", ["domain_id"])
    op.create_index("ix_health_records_institution_id", "health_records", ["institution_id"])


def upgrade() -> None:
    _create_health_domains()
    _create_health_records()


def downgrade() -> None:
    op.drop_index("ix_health_records_institution_id", table_name="health_records")
    op.drop_index("ix_health_records_domain_id", table_name="health_records")
    op.drop_index("ix_health_records_student_id", table_name="health_records")
    op.drop_table("health_records")
    op.drop_index("ix_health_domains_institution_id", table_name="health_domains")
    op.drop_table("health_domains")
