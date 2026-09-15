import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class SupportedEmployment(TenantScoped, Base):
    __tablename__ = "supported_employments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_supported_employments_student_institution",
        ),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    workplace: Mapped[str] = mapped_column(Text, nullable=False, default="")
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    activity_type: Mapped[str] = mapped_column(Text, nullable=False, default="")
    work_process: Mapped[str] = mapped_column(Text, nullable=False, default="")
    work_environment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    required_body_functions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hazards_and_safety: Mapped[str] = mapped_column(Text, nullable=False, default="")
    workplace_contact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    escort_contact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    mobility: Mapped[str] = mapped_column(Text, nullable=False, default="")
    work_hours: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
