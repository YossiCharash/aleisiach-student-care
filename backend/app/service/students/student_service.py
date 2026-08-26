import uuid
from datetime import UTC, datetime

from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.student import Student
from backend.app.schema.routes.student_create_request import StudentCreateRequest
from backend.app.schema.routes.student_response import StudentResponse
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.students.student_access_guard import StudentAccessGuard


class StudentService:
    def __init__(
        self,
        student_repository: StudentRepository,
        class_repository: ClassRepository,
        access_guard: StudentAccessGuard,
    ) -> None:
        self._students = student_repository
        self._classes = class_repository
        self._guard = access_guard

    def create(self, request: StudentCreateRequest) -> StudentResponse:
        if not self._classes.exists(request.class_id):
            raise NotFoundError("class")
        student = Student(full_name=request.full_name, class_id=request.class_id)
        self._students.add(student)
        return StudentResponse.model_validate(student)

    def list_active(self, scope: StudentAccessScope) -> list[StudentResponse]:
        students = self._students_in_scope(scope)
        return [StudentResponse.model_validate(student) for student in students]

    def get(self, student_id: uuid.UUID, scope: StudentAccessScope) -> StudentResponse:
        student = self._guard.require(student_id, scope)
        return StudentResponse.model_validate(student)

    def _students_in_scope(self, scope: StudentAccessScope) -> list[Student]:
        if scope.all_classes:
            return self._students.list_active()
        if scope.class_id is None:
            return []
        return self._students.list_active_by_class(scope.class_id)

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
