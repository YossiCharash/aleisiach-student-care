import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.client.student_details import StudentDetails


class StudentDetailsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, student_id: uuid.UUID) -> StudentDetails | None:
        return self._session.get(StudentDetails, student_id)

    def get_or_create(self, student_id: uuid.UUID) -> tuple[StudentDetails, bool]:
        existing = self.get(student_id)
        if existing is not None:
            return existing, False
        details = StudentDetails(student_id=student_id)
        try:
            with self._session.begin_nested():
                self._session.add(details)
                self._session.flush()
        except IntegrityError:
            raced = self.get(student_id)
            if raced is None:
                raise
            return raced, False
        return details, True

    def flush(self) -> None:
        self._session.flush()
