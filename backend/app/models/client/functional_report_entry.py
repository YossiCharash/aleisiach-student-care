import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class FunctionalReportEntry(TenantScoped, Base):
    __tablename__ = "functional_report_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_functional_report_entries_student_institution",
        ),
        UniqueConstraint(
            "id", "institution_id", name="uq_functional_report_entries_id_institution"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    general_background: Mapped[str] = mapped_column(Text, nullable=False, default="")
    vocational_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    behavioral_emotional_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    communication_social_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    independence_life_skills_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary_recommendations: Mapped[str] = mapped_column(Text, nullable=False, default="")
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
