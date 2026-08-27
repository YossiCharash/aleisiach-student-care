import uuid

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class StudentExtraSection(Base):
    __tablename__ = "student_extra_sections"
    __table_args__ = (UniqueConstraint("student_id", "section_type_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    section_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("extra_section_types.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
