"""institutions: multi-tenancy for every institution-owned table

Revision ID: 0015_institutions
Revises: 0014_audit_auth_events
Create Date: 2026-09-02
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from backend.app.models.client.user_role import UserRole

revision: str = "0015_institutions"
down_revision: str | None = "0014_audit_auth_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_INSTITUTION_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
DEFAULT_INSTITUTION_NAME = "מוסד ראשי"
DEFAULT_INSTITUTION_CODE = "main"

REQUIRED_TENANT_TABLES: tuple[str, ...] = (
    "classes",
    "students",
    "labels",
    "sub_labels",
    "skills",
    "solutions",
    "extra_section_types",
    "detail_options",
    "diagnosis_catalog",
)
OPTIONAL_TENANT_TABLES: tuple[str, ...] = ("users", "audit_logs")

PARENT_UNIQUE_CONSTRAINTS: tuple[tuple[str, str], ...] = (
    ("classes", "uq_classes_id_institution"),
    ("labels", "uq_labels_id_institution"),
    ("sub_labels", "uq_sub_labels_id_institution"),
    ("skills", "uq_skills_id_institution"),
    ("extra_section_types", "uq_extra_section_types_id_institution"),
)

COMPOSITE_FOREIGN_KEYS: tuple[tuple[str, str, str, str, str], ...] = (
    ("students", "fk_students_class_institution", "class_id", "classes", "students_class_id_fkey"),
    ("users", "fk_users_class_institution", "class_id", "classes", "users_class_id_fkey"),
    (
        "sub_labels",
        "fk_sub_labels_label_institution",
        "label_id",
        "labels",
        "sub_labels_label_id_fkey",
    ),
    (
        "skills",
        "fk_skills_sub_label_institution",
        "sub_label_id",
        "sub_labels",
        "skills_sub_label_id_fkey",
    ),
    (
        "solutions",
        "fk_solutions_skill_institution",
        "skill_id",
        "skills",
        "solutions_skill_id_fkey",
    ),
    (
        "extra_section_types",
        "fk_extra_section_types_parent_institution",
        "parent_id",
        "extra_section_types",
        "extra_section_types_parent_id_fkey",
    ),
)

SUPER_ADMIN = f"'{UserRole.SUPER_ADMIN.name}'"
SUPER_ADMIN_HAS_NO_INSTITUTION = (
    f"(role = {SUPER_ADMIN} AND institution_id IS NULL)"
    f" OR (role <> {SUPER_ADMIN} AND institution_id IS NOT NULL)"
)


def upgrade() -> None:
    _create_institutions_table()
    _add_tenant_columns()
    _backfill_default_institution()
    _enforce_tenant_columns()
    _replace_email_uniqueness()
    _replace_detail_option_uniqueness()
    _link_children_to_their_institution()
    op.create_check_constraint(
        "ck_users_super_admin_has_no_institution", "users", SUPER_ADMIN_HAS_NO_INSTITUTION
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_super_admin_has_no_institution", "users", type_="check")
    _unlink_children_from_their_institution()
    _restore_detail_option_uniqueness()
    _restore_email_uniqueness()
    _drop_tenant_columns()
    op.drop_table("institutions")


def _create_institutions_table() -> None:
    op.create_table(
        "institutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_by", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def _add_tenant_columns() -> None:
    for table in REQUIRED_TENANT_TABLES + OPTIONAL_TENANT_TABLES:
        op.add_column(table, sa.Column("institution_id", sa.Uuid(), nullable=True))
        op.create_index(f"ix_{table}_institution_id", table, ["institution_id"])
        op.create_foreign_key(
            f"fk_{table}_institution", table, "institutions", ["institution_id"], ["id"]
        )
    op.create_index("ix_users_class_id", "users", ["class_id"])


def _backfill_default_institution() -> None:
    institutions = sa.table(
        "institutions",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("code", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    op.execute(
        institutions.insert().values(
            id=DEFAULT_INSTITUTION_ID,
            name=DEFAULT_INSTITUTION_NAME,
            code=DEFAULT_INSTITUTION_CODE,
            is_active=True,
            created_at=sa.func.now(),
        )
    )
    for table in REQUIRED_TENANT_TABLES + OPTIONAL_TENANT_TABLES:
        op.execute(
            sa.text(f"UPDATE {table} SET institution_id = :institution").bindparams(
                institution=DEFAULT_INSTITUTION_ID
            )
        )


def _enforce_tenant_columns() -> None:
    for table in REQUIRED_TENANT_TABLES:
        op.alter_column(table, "institution_id", existing_type=sa.Uuid(), nullable=False)


def _replace_email_uniqueness() -> None:
    op.drop_constraint("users_email_key", "users", type_="unique")
    op.create_unique_constraint("uq_users_institution_email", "users", ["institution_id", "email"])
    op.create_index(
        "uq_users_platform_email",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("institution_id IS NULL"),
    )


def _restore_email_uniqueness() -> None:
    op.drop_index("uq_users_platform_email", table_name="users")
    op.drop_constraint("uq_users_institution_email", "users", type_="unique")
    op.create_unique_constraint("users_email_key", "users", ["email"])


def _replace_detail_option_uniqueness() -> None:
    op.drop_constraint("detail_options_field_name_key", "detail_options", type_="unique")
    op.create_unique_constraint(
        "uq_detail_options_institution_field_name",
        "detail_options",
        ["institution_id", "field", "name"],
    )


def _restore_detail_option_uniqueness() -> None:
    op.drop_constraint("uq_detail_options_institution_field_name", "detail_options", type_="unique")
    op.create_unique_constraint(
        "detail_options_field_name_key", "detail_options", ["field", "name"]
    )


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
    op.drop_index("ix_users_class_id", table_name="users")
    for table in REQUIRED_TENANT_TABLES + OPTIONAL_TENANT_TABLES:
        op.drop_constraint(f"fk_{table}_institution", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_institution_id", table_name=table)
        op.drop_column(table, "institution_id")
