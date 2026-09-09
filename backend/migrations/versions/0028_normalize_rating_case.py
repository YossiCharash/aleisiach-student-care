"""normalize solution rating values to the enum's name-based (uppercase) storage

Revision ID: 0028_normalize_rating_case
Revises: 0027_skill_rating_solutions
Create Date: 2026-09-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0028_normalize_rating_case"
down_revision: str | None = "0027_skill_rating_solutions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE solutions SET rating = UPPER(rating) WHERE rating <> UPPER(rating)")


def downgrade() -> None:
    pass
