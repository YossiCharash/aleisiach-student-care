import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class Student(TenantScoped, Base):
    __tablename__ = "students"
    __table_args__ = (
        ForeignKeyConstraint(
            ["class_id", "institution_id"],
            ["classes.id", "classes.institution_id"],
            name="fk_students_class_institution",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    class_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
