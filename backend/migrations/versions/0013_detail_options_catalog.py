"""Editable Tab 4 dropdowns: detail option catalog + widen columns to text

Revision ID: 0013_detail_options_catalog
Revises: 0012_details_profile_sections
Create Date: 2026-09-01
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013_detail_options_catalog"
down_revision: str | None = "0012_details_profile_sections"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEFAULTS: dict[str, tuple[str, ...]] = {
    "idd_severity": ("קלה", "בינונית", "מורכבת"),
    "medication_independence": ("אינו נוטל לבד", "זקוק לתזכורת והשגחה", "עצמאי"),
    "expression_mode": (
        "דיבור מילולי שוטף",
        "מילים בודדות ומשפטים קצרים",
        "ג'סטות ותנועות גוף",
        "שימוש בטאבלט או אייפד",
        "לא ורבלי",
    ),
    "language_comprehension": ("מבין הוראות מורכבות", "מבין רק הוראות פשוטות"),
    "assistive_device": ("משקפיים", "מכשיר שמיעה", "מדרסים", "קביים", "הליכון", "אחר"),
}
_TEXT_COLUMNS = (
    "idd_severity",
    "medication_independence",
    "expression_mode",
    "language_comprehension",
)


def upgrade() -> None:
    options = op.create_table(
        "detail_options",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("field", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("field", "name"),
    )
    rows = [
        {
            "id": uuid.uuid4(),
            "field": field,
            "name": name,
            "order": order,
            "is_active": True,
        }
        for field, names in _DEFAULTS.items()
        for order, name in enumerate(names)
    ]
    op.bulk_insert(options, rows)
    for column in _TEXT_COLUMNS:
        op.alter_column(
            "student_details",
            column,
            type_=sa.String(length=200),
            existing_nullable=True,
        )


def downgrade() -> None:
    for column in _TEXT_COLUMNS:
        op.alter_column(
            "student_details",
            column,
            type_=sa.String(length=32),
            existing_nullable=True,
        )
    op.drop_table("detail_options")
