"""tenant-scope the content tables that hung off a student without an institution

Revision ID: 0018_tenant_scope_content
Revises: 0017_institution_contact
Create Date: 2026-09-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018_tenant_scope_content"
down_revision: str | None = "0017_institution_contact"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TENANT_TABLES: tuple[str, ...] = (
    "student_details",
    "social_notes",
    "student_extra_sections",
    "team_meetings",
    "meeting_entries",
    "meeting_entry_solutions",
)

BACKFILL_FROM_PARENT: tuple[tuple[str, str, str], ...] = (
    ("student_details", "students", "student_id"),
    ("social_notes", "students", "student_id"),
    ("student_extra_sections", "students", "student_id"),
    ("team_meetings", "students", "student_id"),
    ("meeting_entries", "team_meetings", "meeting_id"),
    ("meeting_entry_solutions", "meeting_entries", "meeting_entry_id"),
)

PARENT_UNIQUE_CONSTRAINTS: tuple[tuple[str, str], ...] = (
    ("students", "uq_students_id_institution"),
    ("solutions", "uq_solutions_id_institution"),
    ("team_meetings", "uq_team_meetings_id_institution"),
    ("meeting_entries", "uq_meeting_entries_id_institution"),
)

COMPOSITE_FOREIGN_KEYS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "student_details",
        "fk_student_details_student_institution",
        "student_id",
        "students",
        "student_details_student_id_fkey",
    ),
    (
        "social_notes",
        "fk_social_notes_student_institution",
        "student_id",
        "students",
        "social_notes_student_id_fkey",
    ),
    (
        "student_extra_sections",
        "fk_student_extra_sections_student_institution",
        "student_id",
        "students",
        "student_extra_sections_student_id_fkey",
    ),
    (
        "student_extra_sections",
        "fk_student_extra_sections_section_type_institution",
        "section_type_id",
        "extra_section_types",
        "student_extra_sections_section_type_id_fkey",
    ),
    (
        "team_meetings",
        "fk_team_meetings_student_institution",
        "student_id",
        "students",
        "team_meetings_student_id_fkey",
    ),
    (
        "meeting_entries",
        "fk_meeting_entries_meeting_institution",
        "meeting_id",
        "team_meetings",
        "meeting_entries_meeting_id_fkey",
    ),
    (
        "meeting_entries",
        "fk_meeting_entries_skill_institution",
        "skill_id",
        "skills",
        "meeting_entries_skill_id_fkey",
    ),
    (
        "meeting_entry_solutions",
        "fk_meeting_entry_solutions_entry_institution",
        "meeting_entry_id",
        "meeting_entries",
        "meeting_entry_solutions_meeting_entry_id_fkey",
    ),
    (
        "meeting_entry_solutions",
        "fk_meeting_entry_solutions_solution_institution",
        "solution_id",
        "solutions",
        "meeting_entry_solutions_solution_id_fkey",
    ),
)


def upgrade() -> None:
    _add_tenant_columns()
    _backfill_from_parents()
    _reject_orphans()
    _enforce_tenant_columns()
    _link_children_to_their_institution()


def downgrade() -> None:
    _unlink_children_from_their_institution()
    _drop_tenant_columns()


def _add_tenant_columns() -> None:
    for table in TENANT_TABLES:
        op.add_column(table, sa.Column("institution_id", sa.Uuid(), nullable=True))
        op.create_index(f"ix_{table}_institution_id", table, ["institution_id"])
        op.create_foreign_key(
            f"fk_{table}_institution", table, "institutions", ["institution_id"], ["id"]
        )


def _backfill_from_parents() -> None:
    for table, parent, column in BACKFILL_FROM_PARENT:
        op.execute(
            sa.text(
                f"UPDATE {table} SET institution_id = ("
                f" SELECT institution_id FROM {parent} WHERE {parent}.id = {table}.{column}"
                f")"
            )
        )


def _reject_orphans() -> None:
    for table in TENANT_TABLES:
        count = op.get_bind().scalar(
            sa.text(f"SELECT count(*) FROM {table} WHERE institution_id IS NULL")
        )
        if count:
            raise RuntimeError(
                f"{table}: {count} rows have no institution because their parent row is missing. "
                "Delete or repair those orphans, then re-run this migration."
            )


def _enforce_tenant_columns() -> None:
    for table in TENANT_TABLES:
        op.alter_column(table, "institution_id", existing_type=sa.Uuid(), nullable=False)


def _link_children_to_their_institution() -> None:
    for table, name in PARENT_UNIQUE_CONSTRAINTS:
        op.create_unique_constraint(name, table, ["id", "institution_id"])
    for table, name, column, parent, previous in COMPOSITE_FOREIGN_KEYS:
        op.drop_constraint(previous, table, type_="foreignkey")
        op.create_foreign_key(
            name, table, parent, [column, "institution_id"], ["id", "institution_id"]
        )


def _unlink_children_from_their_institution() -> None:
    for table, name, column, parent, previous in COMPOSITE_FOREIGN_KEYS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(previous, table, parent, [column], ["id"])
    for table, name in PARENT_UNIQUE_CONSTRAINTS:
        op.drop_constraint(name, table, type_="unique")


def _drop_tenant_columns() -> None:
    for table in TENANT_TABLES:
        op.drop_constraint(f"fk_{table}_institution", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_institution_id", table_name=table)
        op.drop_column(table, "institution_id")
