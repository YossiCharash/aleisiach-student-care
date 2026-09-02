import uuid
from datetime import UTC, datetime

from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.schema.routes.student_create_request import StudentCreateRequest
from backend.app.schema.routes.student_response import StudentResponse
from backend.app.schema.routes.student_update_request import StudentUpdateRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard

_ENTITY_TYPE = "student"
_DETAILS_ENTITY_TYPE = "student_details"


class StudentService:
    def __init__(
        self,
        student_repository: StudentRepository,
        class_repository: ClassRepository,
        details_repository: StudentDetailsRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
    ) -> None:
        self._students = student_repository
        self._classes = class_repository
        self._details = details_repository
        self._guard = access_guard
        self._audit = audit_logger

    def create(self, request: StudentCreateRequest, actor_id: uuid.UUID) -> StudentResponse:
        if not self._classes.exists(request.class_id):
            raise NotFoundError("class")
        student = Student(full_name=request.full_name, class_id=request.class_id)
        self._students.add(student)
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=student.id,
                changes=["full_name", "class_id"],
            )
        )
        self._create_initial_details(student.id, request, actor_id)
        return StudentResponse.model_validate(student)

    def _create_initial_details(
        self, student_id: uuid.UUID, request: StudentCreateRequest, actor_id: uuid.UUID
    ) -> None:
        if request.national_id is None and request.date_of_birth is None:
            return
        details, _ = self._details.get_or_create(student_id)
        changes = self._apply_initial_details(details, request)
        self._details.flush()
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE,
                entity_type=_DETAILS_ENTITY_TYPE,
                entity_id=student_id,
                changes=changes,
            )
        )

    def _apply_initial_details(
        self, details: StudentDetails, request: StudentCreateRequest
    ) -> list[str]:
        changes: list[str] = []
        if request.national_id is not None:
            details.national_id = request.national_id
            changes.append("national_id")
        if request.date_of_birth is not None:
            details.date_of_birth = request.date_of_birth
            changes.append("date_of_birth")
        return changes

    def update(
        self, student_id: uuid.UUID, request: StudentUpdateRequest, actor_id: uuid.UUID
    ) -> StudentResponse:
        student = self._require(student_id)
        if not self._classes.exists(request.class_id):
            raise NotFoundError("class")
        changes = self._apply_update(student, request)
        if changes:
            self._audit.record(
                AuditEntry(
                    actor_id=actor_id,
                    action=AuditAction.UPDATE,
                    entity_type=_ENTITY_TYPE,
                    entity_id=student.id,
                    changes=changes,
                )
            )
        return StudentResponse.model_validate(student)

    def _apply_update(self, student: Student, request: StudentUpdateRequest) -> list[str]:
        changes: list[str] = []
        if student.full_name != request.full_name:
            student.full_name = request.full_name
            changes.append("full_name")
        if student.class_id != request.class_id:
            student.class_id = request.class_id
            changes.append("class_id")
        return changes

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

    def archive(self, student_id: uuid.UUID, archived_by: uuid.UUID) -> StudentResponse:
        student = self._require(student_id)
        student.is_archived = True
        student.archived_at = datetime.now(UTC)
        student.archived_by = archived_by
        self._audit.record(
            AuditEntry(
                actor_id=archived_by,
                action=AuditAction.ARCHIVE,
                entity_type=_ENTITY_TYPE,
                entity_id=student.id,
                changes=["is_archived"],
            )
        )
        return StudentResponse.model_validate(student)

    def list_archived(self) -> list[StudentResponse]:
        students = self._students.list_archived()
        return [StudentResponse.model_validate(student) for student in students]

    def restore(self, student_id: uuid.UUID, actor_id: uuid.UUID) -> StudentResponse:
        student = self._require(student_id)
        student.is_archived = False
        student.archived_at = None
        student.archived_by = None
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=student.id,
                changes=["is_archived"],
            )
        )
        return StudentResponse.model_validate(student)

    def _require(self, student_id: uuid.UUID) -> Student:
        student = self._students.get(student_id)
        if student is None:
            raise NotFoundError("student")
        return student
