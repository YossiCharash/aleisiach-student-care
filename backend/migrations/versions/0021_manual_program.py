"""manual promotion program, entries, and chosen solutions (Tab 2)

Revision ID: 0021_manual_program
Revises: 0020_details_extra_fields
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0021_manual_program"
down_revision: str | None = "0020_details_extra_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "programs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_programs_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", name="uq_programs_student"),
        sa.UniqueConstraint("id", "institution_id", name="uq_programs_id_institution"),
    )
    op.create_index("ix_programs_student_id", "programs", ["student_id"])
    op.create_index("ix_programs_institution_id", "programs", ["institution_id"])
    op.create_table(
        "program_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("program_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("skill_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["program_id", "institution_id"],
            ["programs.id", "programs.institution_id"],
            name="fk_program_entries_program_institution",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_program_entries_skill_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_program_entries_id_institution"),
    )
    op.create_index("ix_program_entries_program_id", "program_entries", ["program_id"])
    op.create_index("ix_program_entries_institution_id", "program_entries", ["institution_id"])
    op.create_table(
        "program_entry_solutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("program_entry_id", sa.Uuid(), nullable=False),
        sa.Column("solution_id", sa.Uuid(), nullable=False),
        sa.Column("solution_text_snapshot", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["program_entry_id", "institution_id"],
            ["program_entries.id", "program_entries.institution_id"],
            name="fk_program_entry_solutions_entry_institution",
        ),
        sa.ForeignKeyConstraint(
            ["solution_id", "institution_id"],
            ["solutions.id", "solutions.institution_id"],
            name="fk_program_entry_solutions_solution_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_program_entry_solutions_program_entry_id",
        "program_entry_solutions",
        ["program_entry_id"],
    )
    op.create_index(
        "ix_program_entry_solutions_institution_id",
        "program_entry_solutions",
        ["institution_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_program_entry_solutions_institution_id",
        table_name="program_entry_solutions",
    )
    op.drop_index(
        "ix_program_entry_solutions_program_entry_id",
        table_name="program_entry_solutions",
    )
    op.drop_table("program_entry_solutions")
    op.drop_index("ix_program_entries_institution_id", table_name="program_entries")
    op.drop_index("ix_program_entries_program_id", table_name="program_entries")
    op.drop_table("program_entries")
    op.drop_index("ix_programs_institution_id", table_name="programs")
    op.drop_index("ix_programs_student_id", table_name="programs")
    op.drop_table("programs")
