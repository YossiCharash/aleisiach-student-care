import uuid

from sqlalchemy import Enum, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program_plan_solution import ProgramPlanSolution
from backend.app.models.client.tenant_scoped import TenantScoped


class ProgramPlanEntry(TenantScoped, Base):
    __tablename__ = "program_plan_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["plan_id", "institution_id"],
            ["program_plans.id", "program_plans.institution_id"],
            name="fk_program_plan_entries_plan_institution",
        ),
        ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_program_plan_entries_skill_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_program_plan_entries_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    skill_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    rating: Mapped[MeetingRating] = mapped_column(
        Enum(MeetingRating, native_enum=False, length=16), nullable=False
    )
    position: Mapped[int] = mapped_column("position", Integer, nullable=False)
    solutions: Mapped[list[ProgramPlanSolution]] = relationship(
        cascade="all, delete-orphan", order_by=ProgramPlanSolution.position
    )
