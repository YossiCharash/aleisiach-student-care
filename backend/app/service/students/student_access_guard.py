import uuid

from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.student import Student
from backend.app.schema.service.student_access_scope import StudentAccessScope


class StudentAccessGuard:
    def __init__(self, student_repository: StudentRepository) -> None:
        self._students = student_repository

    def require(self, student_id: uuid.UUID, scope: StudentAccessScope) -> Student:
        student = self._students.get(student_id)
        if student is None or not scope.permits(student.class_id):
            raise NotFoundError("student")
        return student
