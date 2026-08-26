"""taxonomy: labels, sub-labels, skills, solutions

Revision ID: 0004_taxonomy
Revises: 0003_sessions
Create Date: 2026-08-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_taxonomy"
down_revision: str | None = "0003_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "labels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sub_labels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("label_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sub_labels_label_id", "sub_labels", ["label_id"])
    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sub_label_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["sub_label_id"], ["sub_labels.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skills_sub_label_id", "skills", ["sub_label_id"])
    op.create_table(
        "solutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_solutions_skill_id", "solutions", ["skill_id"])


def downgrade() -> None:
    op.drop_index("ix_solutions_skill_id", table_name="solutions")
    op.drop_table("solutions")
    op.drop_index("ix_skills_sub_label_id", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_sub_labels_label_id", table_name="sub_labels")
    op.drop_table("sub_labels")
    op.drop_table("labels")
