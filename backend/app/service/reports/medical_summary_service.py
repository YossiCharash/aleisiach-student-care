import uuid

from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.medical_summary import MedicalSummary
from backend.app.models.client.student import Student
from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields
from backend.app.schema.routes.medical_summary_response import MedicalSummaryResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "medical_summary"


class MedicalSummaryService:
    def __init__(
        self,
        summary_repository: MedicalSummaryRepository,
        details_repository: StudentDetailsRepository,
        user_repository: UserRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._summaries = summary_repository
        self._details = details_repository
        self._users = user_repository
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

    def get(self, student_id: uuid.UUID, scope: StudentAccessScope) -> MedicalSummaryResponse:
        student = self._guard.require(student_id, scope)
        return self._to_response(student, self._summaries.get(student_id))

    def upsert(
        self,
        student_id: uuid.UUID,
        request: MedicalSummaryFields,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> MedicalSummaryResponse:
        student = self._guard.require(student_id, scope)
        summary = self._summaries.get(student_id)
        created = False
        if summary is None:
            summary, created = self._summaries.create(self._build(student_id, request, actor_id))
        if created:
            changes = list(self._fields())
        else:
            changes = self._changed(summary, request)
            self._apply(summary, request, actor_id)
            self._summaries.flush()
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE if created else AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=student_id,
                changes=changes,
            )
        )
        return self._to_response(student, summary)

    def _fields(self) -> tuple[str, ...]:
        return MedicalSummaryFields.field_names()

    def _changed(self, summary: MedicalSummary, request: MedicalSummaryFields) -> list[str]:
        return [name for name in self._fields() if getattr(summary, name) != getattr(request, name)]

    def _build(
        self, student_id: uuid.UUID, request: MedicalSummaryFields, actor_id: uuid.UUID
    ) -> MedicalSummary:
        summary = MedicalSummary(student_id=student_id)
        self._apply(summary, request, actor_id)
        return summary

    def _apply(
        self, summary: MedicalSummary, request: MedicalSummaryFields, actor_id: uuid.UUID
    ) -> None:
        for name in self._fields():
            setattr(summary, name, getattr(request, name))
        summary.updated_by = actor_id
        summary.updated_at = self._clock.now()

    def _to_response(
        self, student: Student, summary: MedicalSummary | None
    ) -> MedicalSummaryResponse:
        details = self._details.get(student.id)
        identity = {
            "student_id": student.id,
            "student_name": student.full_name,
            "national_id": details.national_id if details is not None else None,
            "date_of_birth": details.date_of_birth if details is not None else None,
            "address": details.address if details is not None else None,
        }
        if summary is None:
            return MedicalSummaryResponse(exists=False, **identity)
        writer = self._users.get(summary.updated_by)
        return MedicalSummaryResponse(
            exists=True,
            written_by_name=writer.full_name if writer is not None else None,
            updated_at=summary.updated_at,
            **identity,
            **{name: getattr(summary, name) for name in self._fields()},
        )
