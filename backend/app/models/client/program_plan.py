import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.client.program_plan_entry import ProgramPlanEntry
from backend.app.models.client.tenant_scoped import TenantScoped


class ProgramPlan(TenantScoped, Base):
    __tablename__ = "program_plans"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_program_plans_student_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_program_plans_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    entries: Mapped[list[ProgramPlanEntry]] = relationship(
        cascade="all, delete-orphan", order_by=ProgramPlanEntry.position
    )
