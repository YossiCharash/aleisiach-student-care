import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.optional_tenant_scoped import OptionalTenantScoped


class AuditLog(OptionalTenantScoped, Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, native_enum=False, length=32), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    changes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(400), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
