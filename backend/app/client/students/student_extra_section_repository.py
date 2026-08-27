import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.client.student_extra_section import StudentExtraSection


class StudentExtraSectionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, student_id: uuid.UUID, section_type_id: uuid.UUID) -> StudentExtraSection | None:
        statement = select(StudentExtraSection).where(
            StudentExtraSection.student_id == student_id,
            StudentExtraSection.section_type_id == section_type_id,
        )
        return self._session.scalar(statement)

    def list_for_student(self, student_id: uuid.UUID) -> list[StudentExtraSection]:
        statement = select(StudentExtraSection).where(StudentExtraSection.student_id == student_id)
        return list(self._session.scalars(statement).all())

    def create(self, entry: StudentExtraSection) -> tuple[StudentExtraSection, bool]:
        try:
            with self._session.begin_nested():
                self._session.add(entry)
                self._session.flush()
        except IntegrityError:
            existing = self.get(entry.student_id, entry.section_type_id)
            if existing is None:
                raise
            return existing, False
        return entry, True

    def flush(self) -> None:
        self._session.flush()
