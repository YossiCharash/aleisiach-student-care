"""rename classes to workshops, add workshop color

Revision ID: 0026_workshops
Revises: 0025_meeting_snapshots
Create Date: 2026-09-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0026_workshops"
down_revision: str | None = "0025_meeting_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("classes", "workshops")
    op.execute(
        "ALTER TABLE workshops RENAME CONSTRAINT "
        "uq_classes_id_institution TO uq_workshops_id_institution"
    )
    op.add_column(
        "workshops",
        sa.Column("color", sa.String(length=7), nullable=False, server_default="#3F8420"),
    )
    op.alter_column("students", "class_id", new_column_name="workshop_id")
    op.alter_column("users", "class_id", new_column_name="workshop_id")
    op.execute(
        "ALTER TABLE students RENAME CONSTRAINT "
        "fk_students_class_institution TO fk_students_workshop_institution"
    )
    op.execute(
        "ALTER TABLE users RENAME CONSTRAINT "
        "fk_users_class_institution TO fk_users_workshop_institution"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users RENAME CONSTRAINT "
        "fk_users_workshop_institution TO fk_users_class_institution"
    )
    op.execute(
        "ALTER TABLE students RENAME CONSTRAINT "
        "fk_students_workshop_institution TO fk_students_class_institution"
    )
    op.alter_column("users", "workshop_id", new_column_name="class_id")
    op.alter_column("students", "workshop_id", new_column_name="class_id")
    op.drop_column("workshops", "color")
    op.execute(
        "ALTER TABLE workshops RENAME CONSTRAINT "
        "uq_workshops_id_institution TO uq_classes_id_institution"
    )
    op.rename_table("workshops", "classes")
