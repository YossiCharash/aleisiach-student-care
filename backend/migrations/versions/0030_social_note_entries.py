"""social worker note (Tab 3) becomes a dated, archivable series of entries

Revision ID: 0030_social_note_entries
Revises: 0029_flatten_skills_to_labels
Create Date: 2026-09-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0030_social_note_entries"
down_revision: str | None = "0029_flatten_skills_to_labels"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("social_notes")

    op.create_table(
        "social_note_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("note_date", sa.Date(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
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
            name="fk_social_note_entries_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_social_note_entries_id_institution"),
    )
    op.create_index("ix_social_note_entries_student_id", "social_note_entries", ["student_id"])
    op.create_index(
        "ix_social_note_entries_institution_id", "social_note_entries", ["institution_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_social_note_entries_institution_id", table_name="social_note_entries")
    op.drop_index("ix_social_note_entries_student_id", table_name="social_note_entries")
    op.drop_table("social_note_entries")

    op.create_table(
        "social_notes",
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_social_notes_student_institution",
        ),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index("ix_social_notes_institution_id", "social_notes", ["institution_id"])
