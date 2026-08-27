"""Tab 4 extra sections: configurable section types + per-student content

Revision ID: 0010_extra_sections
Revises: 0009_login_lockout
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_extra_sections"
down_revision: str | None = "0009_login_lockout"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "extra_section_types",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["extra_section_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_extra_section_types_parent_id", "extra_section_types", ["parent_id"])
    op.create_table(
        "student_extra_sections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("section_type_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["section_type_id"], ["extra_section_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "section_type_id"),
    )
    op.create_index(
        "ix_student_extra_sections_student_id",
        "student_extra_sections",
        ["student_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_student_extra_sections_student_id", table_name="student_extra_sections")
    op.drop_table("student_extra_sections")
    op.drop_index("ix_extra_section_types_parent_id", table_name="extra_section_types")
    op.drop_table("extra_section_types")
