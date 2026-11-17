"""student details: optional phone number

Revision ID: 0045_student_phone
Revises: 0044_employment_work_style
Create Date: 2026-11-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0045_student_phone"
down_revision: str | None = "0044_employment_work_style"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "student_details",
        sa.Column("phone", sa.String(length=40), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("student_details", "phone")
