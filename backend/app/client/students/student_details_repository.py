import uuid

from sqlalchemy.orm import Session

from backend.app.models.client.student_details import StudentDetails


class StudentDetailsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, student_id: uuid.UUID) -> StudentDetails | None:
        return self._session.get(StudentDetails, student_id)

    def add(self, details: StudentDetails) -> StudentDetails:
        self._session.add(details)
        self._session.flush()
        return details
