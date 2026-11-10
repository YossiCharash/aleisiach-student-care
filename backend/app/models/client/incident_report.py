import uuid
from datetime import UTC, date, datetime, time

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.incident_report_type import IncidentReportType
from backend.app.models.client.tenant_scoped import TenantScoped


class IncidentReport(TenantScoped, Base):
    __tablename__ = "incident_reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_incident_reports_student_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_incident_reports_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    location: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reporter_name_role: Mapped[str] = mapped_column(Text, nullable=False, default="")
    report_type: Mapped[IncidentReportType | None] = mapped_column(
        Enum(IncidentReportType, native_enum=False, length=16), nullable=True
    )
    natures: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    nature_other: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    staff_present: Mapped[str] = mapped_column(Text, nullable=False, default="")
    affected_service_recipients: Mapped[str] = mapped_column(Text, nullable=False, default="")
    warning_signs: Mapped[str] = mapped_column(Text, nullable=False, default="")
    actions_taken: Mapped[str] = mapped_column(Text, nullable=False, default="")
    referrals: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    referral_other: Mapped[str] = mapped_column(Text, nullable=False, default="")
    decision_reasons: Mapped[str] = mapped_column(Text, nullable=False, default="")
    manager_updated_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    manager_updated_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    incident_causes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    was_preventable: Mapped[str] = mapped_column(Text, nullable=False, default="")
    lessons_learned: Mapped[str] = mapped_column(Text, nullable=False, default="")
    corrective_action_plan: Mapped[str] = mapped_column(Text, nullable=False, default="")
    filler_role: Mapped[str] = mapped_column(Text, nullable=False, default="")
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
