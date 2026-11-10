"""risk management: institution risk domains + a dated, archivable risk table per student

Revision ID: 0040_risk_assessments
Revises: 0039_medical_summaries
Create Date: 2026-11-10
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0040_risk_assessments"
down_revision: str | None = "0039_medical_summaries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEFAULT_DOMAINS: tuple[tuple[str, str], ...] = (
    (
        "medical",
        "אכילה, שתיה ובליעה (חנק, חסר שיניים, קצב מהיר, מזון מרוסק, חטיפת אוכל, שתיה, "
        "רגישויות, אלרגיות)",
    ),
    ("medical", "עודף / חוסר משקל"),
    ("medical", "אפילפסיה / סוכרת / אסטמה"),
    ("medical", "סרבנות לטיפול רפואי (תרופות, בדיקות דם, ביקור רופא וכו׳)"),
    ("medical", "אי יציבות (נפילות, נעליים מיוחדות)"),
    ("behavioral", "בריחות ו/או שוטטות"),
    ("behavioral", "פגיעה עצמית / פגיעה בסביבה / פגיעה ברכוש"),
    ("behavioral", "התנהגות כפייתית"),
    ("behavioral", "סיכון בתחום המיני-חברתי (פוגע / נפגע)"),
    ("behavioral", "התנהגות קרבנית"),
    ("independence", "ניידות בקהילה"),
    ("independence", "התמצאות במרחב, שימוש בתחבורה, חצית כבישים"),
    ("independence", "השארות בדירה באופן עצמאי"),
    ("independence", "שהות ברחבי המרכז ללא השגחה צמודה"),
    ("independence", "לקיחת תרופות באופן עצמאי"),
    ("independence", "שימוש בחומרי ניקוי וכלי מטבח חדים"),
    ("independence", "סיכון ביציאה עצמאית מהמרכז"),
)


def _default_rows(institution_id: uuid.UUID) -> list[dict[str, object]]:
    orders: dict[str, int] = {}
    rows: list[dict[str, object]] = []
    for category, name in _DEFAULT_DOMAINS:
        order = orders.get(category, 0)
        orders[category] = order + 1
        rows.append(
            {
                "id": uuid.uuid4(),
                "name": name,
                "category": category,
                "order": order,
                "is_active": True,
                "institution_id": institution_id,
            }
        )
    return rows


def _create_risk_domains() -> None:
    domains = op.create_table(
        "risk_domains",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=16), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_risk_domains_id_institution"),
    )
    op.create_index("ix_risk_domains_institution_id", "risk_domains", ["institution_id"])
    institution_ids = op.get_bind().scalars(sa.text("SELECT id FROM institutions")).all()
    rows = [row for institution_id in institution_ids for row in _default_rows(institution_id)]
    if rows:
        op.bulk_insert(domains, rows)


def _create_risk_assessments() -> None:
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("assessment_date", sa.Date(), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
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
            name="fk_risk_assessments_student_institution",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "institution_id", name="uq_risk_assessments_id_institution"),
    )
    op.create_index("ix_risk_assessments_student_id", "risk_assessments", ["student_id"])
    op.create_index("ix_risk_assessments_institution_id", "risk_assessments", ["institution_id"])


def upgrade() -> None:
    _create_risk_domains()
    _create_risk_assessments()


def downgrade() -> None:
    op.drop_index("ix_risk_assessments_institution_id", table_name="risk_assessments")
    op.drop_index("ix_risk_assessments_student_id", table_name="risk_assessments")
    op.drop_table("risk_assessments")
    op.drop_index("ix_risk_domains_institution_id", table_name="risk_domains")
    op.drop_table("risk_domains")
