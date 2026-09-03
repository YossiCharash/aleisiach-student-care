import uuid

from sqlalchemy import ForeignKeyConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class StudentExtraSection(TenantScoped, Base):
    __tablename__ = "student_extra_sections"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_student_extra_sections_student_institution",
        ),
        ForeignKeyConstraint(
            ["section_type_id", "institution_id"],
            ["extra_section_types.id", "extra_section_types.institution_id"],
            name="fk_student_extra_sections_section_type_institution",
        ),
        UniqueConstraint("student_id", "section_type_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    section_type_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
