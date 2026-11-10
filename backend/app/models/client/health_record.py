import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.health_session_type import HealthSessionType
from backend.app.models.client.tenant_scoped import TenantScoped


class HealthRecord(TenantScoped, Base):
    __tablename__ = "health_records"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_health_records_student_institution",
        ),
        ForeignKeyConstraint(
            ["domain_id", "institution_id"],
            ["health_domains.id", "health_domains.institution_id"],
            name="fk_health_records_domain_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_health_records_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    domain_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    session_type: Mapped[HealthSessionType | None] = mapped_column(
        Enum(HealthSessionType, native_enum=False, length=16), nullable=True
    )
    support_given: Mapped[str] = mapped_column(Text, nullable=False, default="")
    responsible_user_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    execution_review: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
