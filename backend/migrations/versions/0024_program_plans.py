"""split foci from solutions; add dated, versioned program plans (Tab 1)

Revision ID: 0024_program_plans
Revises: 0023_details_institutions
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0024_program_plans"
down_revision: str | None = "0023_details_institutions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        "ix_program_entry_solutions_institution_id",
        table_name="program_entry_solutions",
    )
    op.drop_index(
        "ix_program_entry_solutions_program_entry_id",
        table_name="program_entry_solutions",
    )
    op.drop_table("program_entry_solutions")

    op.create_table(
        "program_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_program_plans_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_program_plans_id_institution"),
    )
    op.create_index("ix_program_plans_student_id", "program_plans", ["student_id"])
    op.create_index("ix_program_plans_institution_id", "program_plans", ["institution_id"])

    op.create_table(
        "program_plan_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("skill_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["plan_id", "institution_id"],
            ["program_plans.id", "program_plans.institution_id"],
            name="fk_program_plan_entries_plan_institution",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_program_plan_entries_skill_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_program_plan_entries_id_institution"),
    )
    op.create_index("ix_program_plan_entries_plan_id", "program_plan_entries", ["plan_id"])
    op.create_index(
        "ix_program_plan_entries_institution_id", "program_plan_entries", ["institution_id"]
    )

    op.create_table(
        "program_plan_solutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_entry_id", sa.Uuid(), nullable=False),
        sa.Column("solution_id", sa.Uuid(), nullable=False),
        sa.Column("solution_text_snapshot", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["plan_entry_id", "institution_id"],
            ["program_plan_entries.id", "program_plan_entries.institution_id"],
            name="fk_program_plan_solutions_entry_institution",
        ),
        sa.ForeignKeyConstraint(
            ["solution_id", "institution_id"],
            ["solutions.id", "solutions.institution_id"],
            name="fk_program_plan_solutions_solution_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_program_plan_solutions_plan_entry_id",
        "program_plan_solutions",
        ["plan_entry_id"],
    )
    op.create_index(
        "ix_program_plan_solutions_institution_id",
        "program_plan_solutions",
        ["institution_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_program_plan_solutions_institution_id", table_name="program_plan_solutions")
    op.drop_index("ix_program_plan_solutions_plan_entry_id", table_name="program_plan_solutions")
    op.drop_table("program_plan_solutions")
    op.drop_index("ix_program_plan_entries_institution_id", table_name="program_plan_entries")
    op.drop_index("ix_program_plan_entries_plan_id", table_name="program_plan_entries")
    op.drop_table("program_plan_entries")
    op.drop_index("ix_program_plans_institution_id", table_name="program_plans")
    op.drop_index("ix_program_plans_student_id", table_name="program_plans")
    op.drop_table("program_plans")

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
