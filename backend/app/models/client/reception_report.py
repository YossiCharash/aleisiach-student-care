import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, ForeignKeyConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class ReceptionReport(TenantScoped, Base):
    __tablename__ = "reception_reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_reception_reports_student_institution",
        ),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    committee_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    committee_participants: Mapped[str] = mapped_column(Text, nullable=False, default="")
    intake_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    committee_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    committee_recommendations: Mapped[str] = mapped_column(Text, nullable=False, default="")
    framework_code: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    tariff_code: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    committee_held: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    committee_held_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    director_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    director_approval_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    family_guardian_housing_updated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    family_guardian_housing_updated_note: Mapped[str] = mapped_column(
        Text, nullable=False, default=""
    )
    community_social_worker_updated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    community_social_worker_updated_note: Mapped[str] = mapped_column(
        Text, nullable=False, default=""
    )
    management_updated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    management_updated_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
