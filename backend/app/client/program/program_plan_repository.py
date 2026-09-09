import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.client.program_plan import ProgramPlan
from backend.app.models.client.program_plan_entry import ProgramPlanEntry


class ProgramPlanRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, plan: ProgramPlan) -> ProgramPlan:
        self._session.add(plan)
        self._session.flush()
        return plan

    def get(self, plan_id: uuid.UUID) -> ProgramPlan | None:
        statement = (
            select(ProgramPlan)
            .where(ProgramPlan.id == plan_id)
            .options(selectinload(ProgramPlan.entries).selectinload(ProgramPlanEntry.solutions))
        )
        return self._session.scalars(statement).one_or_none()

    def list_for_student(self, student_id: uuid.UUID) -> list[ProgramPlan]:
        statement = (
            select(ProgramPlan)
            .where(ProgramPlan.student_id == student_id)
            .order_by(ProgramPlan.created_at.desc(), ProgramPlan.id.desc())
            .options(selectinload(ProgramPlan.entries).selectinload(ProgramPlanEntry.solutions))
        )
        return list(self._session.scalars(statement).all())
