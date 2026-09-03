import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class SocialNote(TenantScoped, Base):
    __tablename__ = "social_notes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_social_notes_student_institution",
        ),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
