import uuid
from datetime import UTC, datetime

from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.student import Student
from backend.app.schema.routes.student_create_request import StudentCreateRequest
from backend.app.schema.routes.student_response import StudentResponse


class StudentService:
    def __init__(
        self,
        student_repository: StudentRepository,
        class_repository: ClassRepository,
    ) -> None:
        self._students = student_repository
        self._classes = class_repository

    def create(self, request: StudentCreateRequest) -> StudentResponse:
        if not self._classes.exists(request.class_id):
            raise NotFoundError("class")
        student = Student(full_name=request.full_name, class_id=request.class_id)
        self._students.add(student)
        return StudentResponse.model_validate(student)

    def list_active(self) -> list[StudentResponse]:
        return [StudentResponse.model_validate(student) for student in self._students.list_active()]

    def get(self, student_id: uuid.UUID) -> StudentResponse:
        student = self._require(student_id)
        return StudentResponse.model_validate(student)

    def archive(
        self, student_id: uuid.UUID, archived_by: uuid.UUID | None = None
    ) -> StudentResponse:
        student = self._require(student_id)
        student.is_archived = True
        student.archived_at = datetime.now(UTC)
        student.archived_by = archived_by
        return StudentResponse.model_validate(student)

    def _require(self, student_id: uuid.UUID) -> Student:
        student = self._students.get(student_id)
        if student is None:
            raise NotFoundError("student")
        return student
