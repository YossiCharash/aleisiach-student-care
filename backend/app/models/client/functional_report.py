import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class FunctionalReport(TenantScoped, Base):
    __tablename__ = "functional_reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_functional_reports_student_institution",
        ),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    general_background: Mapped[str] = mapped_column(Text, nullable=False, default="")
    vocational_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    behavioral_emotional_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    communication_social_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    independence_life_skills_domain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary_recommendations: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
