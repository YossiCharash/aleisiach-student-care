import uuid

from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.medical_summary_entry import MedicalSummaryEntry
from backend.app.models.client.student import Student
from backend.app.schema.routes.medical_summary_create_request import MedicalSummaryCreateRequest
from backend.app.schema.routes.medical_summary_entry_response import MedicalSummaryEntryResponse
from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields
from backend.app.schema.routes.medical_summary_history_response import (
    MedicalSummaryHistoryResponse,
)
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

    def history(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> MedicalSummaryHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, self._summaries.list_for_student(student_id))

    def entry_history(
        self, student_id: uuid.UUID, entry_id: uuid.UUID, scope: StudentAccessScope
    ) -> MedicalSummaryHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, [self._require_entry(student_id, entry_id)])

    def create(
        self,
        student_id: uuid.UUID,
        request: MedicalSummaryCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> MedicalSummaryEntryResponse:
        self._guard.require(student_id, scope)
        entry = MedicalSummaryEntry(
            student_id=student_id, summary_date=request.summary_date, author_id=author_id
        )
        self._apply(entry, request)
        self._summaries.add(entry)
        self._record(author_id, AuditAction.CREATE, entry.id, ["summary_date", *self._fields()])
        return self._to_response(entry)

    def update(
        self,
        student_id: uuid.UUID,
        entry_id: uuid.UUID,
        request: MedicalSummaryFields,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> MedicalSummaryEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        changes = self._changed(entry, request)
        self._apply(entry, request)
        self._summaries.flush()
        if changes:
            self._record(actor_id, AuditAction.UPDATE, entry.id, changes)
        return self._to_response(entry)

    def archive(
        self,
        student_id: uuid.UUID,
        entry_id: uuid.UUID,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> MedicalSummaryEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        entry.is_archived = True
        entry.archived_at = self._clock.now()
        entry.archived_by = actor_id
        self._summaries.flush()
        self._record(actor_id, AuditAction.ARCHIVE, entry.id, ["is_archived"])
        return self._to_response(entry)

    def _fields(self) -> tuple[str, ...]:
        return MedicalSummaryFields.field_names()

    def _changed(self, entry: MedicalSummaryEntry, request: MedicalSummaryFields) -> list[str]:
        return [name for name in self._fields() if getattr(entry, name) != getattr(request, name)]

    def _apply(self, entry: MedicalSummaryEntry, request: MedicalSummaryFields) -> None:
        for name in self._fields():
            setattr(entry, name, getattr(request, name))

    def _record(
        self, actor_id: uuid.UUID, action: AuditAction, entry_id: uuid.UUID, changes: list[str]
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=entry_id,
                changes=changes,
            )
        )

    def _require_entry(self, student_id: uuid.UUID, entry_id: uuid.UUID) -> MedicalSummaryEntry:
        entry = self._summaries.get(entry_id)
        if entry is None or entry.student_id != student_id or entry.is_archived:
            raise NotFoundError("medical_summary")
        return entry

    def _build_history(
        self, student: Student, entries: list[MedicalSummaryEntry]
    ) -> MedicalSummaryHistoryResponse:
        details = self._details.get(student.id)
        author_names: dict[uuid.UUID, str | None] = {}
        return MedicalSummaryHistoryResponse(
            student_id=student.id,
            student_name=student.full_name,
            national_id=details.national_id if details is not None else None,
            date_of_birth=details.date_of_birth if details is not None else None,
            address=details.address if details is not None else None,
            entries=[self._to_response(entry, author_names) for entry in entries],
        )

    def _to_response(
        self,
        entry: MedicalSummaryEntry,
        author_names: dict[uuid.UUID, str | None] | None = None,
    ) -> MedicalSummaryEntryResponse:
        return MedicalSummaryEntryResponse(
            id=entry.id,
            student_id=entry.student_id,
            summary_date=entry.summary_date,
            author_id=entry.author_id,
            author_name=self._author_name(entry.author_id, author_names),
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            **{name: getattr(entry, name) for name in self._fields()},
        )

    def _author_name(
        self,
        author_id: uuid.UUID,
        cache: dict[uuid.UUID, str | None] | None = None,
    ) -> str | None:
        if cache is not None and author_id in cache:
            return cache[author_id]
        user = self._users.get(author_id)
        name = user.full_name if user is not None else None
        if cache is not None:
            cache[author_id] = name
        return name
