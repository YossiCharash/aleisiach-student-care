import uuid

from sqlalchemy import ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class ProgramPlanSolution(TenantScoped, Base):
    __tablename__ = "program_plan_solutions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["plan_entry_id", "institution_id"],
            ["program_plan_entries.id", "program_plan_entries.institution_id"],
            name="fk_program_plan_solutions_entry_institution",
        ),
        ForeignKeyConstraint(
            ["solution_id", "institution_id"],
            ["solutions.id", "solutions.institution_id"],
            name="fk_program_plan_solutions_solution_institution",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    plan_entry_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    solution_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    solution_text_snapshot: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column("position", Integer, nullable=False)
