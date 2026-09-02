import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.optional_tenant_scoped import OptionalTenantScoped
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus

_PLATFORM_ACCOUNT = text("institution_id IS NULL")
_SUPER_ADMIN = f"'{UserRole.SUPER_ADMIN.name}'"


class User(OptionalTenantScoped, Base):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(
            ["class_id", "institution_id"],
            ["classes.id", "classes.institution_id"],
            name="fk_users_class_institution",
        ),
        CheckConstraint(
            f"(role = {_SUPER_ADMIN} AND institution_id IS NULL)"
            f" OR (role <> {_SUPER_ADMIN} AND institution_id IS NOT NULL)",
            name="ck_users_super_admin_has_no_institution",
        ),
        UniqueConstraint("institution_id", "email", name="uq_users_institution_email"),
        Index(
            "uq_users_platform_email",
            "email",
            unique=True,
            postgresql_where=_PLATFORM_ACCOUNT,
            sqlite_where=_PLATFORM_ACCOUNT,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    username: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=32), nullable=False
    )
    class_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, native_enum=False, length=16),
        default=UserStatus.INVITED,
        nullable=False,
    )
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reset_request_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
