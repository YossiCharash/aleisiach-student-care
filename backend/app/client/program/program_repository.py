import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.client.program import Program
from backend.app.models.client.program_entry import ProgramEntry


class ProgramRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, program: Program) -> Program:
        self._session.add(program)
        self._session.flush()
        return program

    def flush(self) -> None:
        self._session.flush()

    def get_for_student(self, student_id: uuid.UUID) -> Program | None:
        statement = (
            select(Program)
            .where(Program.student_id == student_id)
            .options(selectinload(Program.entries).selectinload(ProgramEntry.solutions))
        )
        return self._session.scalars(statement).one_or_none()
