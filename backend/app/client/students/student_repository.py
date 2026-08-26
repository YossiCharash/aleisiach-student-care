import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.student import Student


class StudentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, student: Student) -> Student:
        self._session.add(student)
        self._session.flush()
        return student

    def get(self, student_id: uuid.UUID) -> Student | None:
        return self._session.get(Student, student_id)

    def list_active(self) -> list[Student]:
        statement = (
            select(Student).where(Student.is_archived.is_(False)).order_by(Student.full_name)
        )
        return list(self._session.scalars(statement).all())

    def list_active_by_class(self, class_id: uuid.UUID) -> list[Student]:
        statement = (
            select(Student)
            .where(Student.is_archived.is_(False), Student.class_id == class_id)
            .order_by(Student.full_name)
        )
        return list(self._session.scalars(statement).all())
