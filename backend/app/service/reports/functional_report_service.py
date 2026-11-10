import uuid

from backend.app.client.reports.functional_report_repository import FunctionalReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.functional_report_entry import FunctionalReportEntry
from backend.app.models.client.student import Student
from backend.app.schema.routes.functional_report_create_request import (
    FunctionalReportCreateRequest,
)
from backend.app.schema.routes.functional_report_entry_response import (
    FunctionalReportEntryResponse,
)
from backend.app.schema.routes.functional_report_history_response import (
    FunctionalReportHistoryResponse,
)
from backend.app.schema.routes.functional_report_sections import FunctionalReportSections
from backend.app.schema.routes.functional_report_update_request import (
    FunctionalReportUpdateRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "functional_report"


class FunctionalReportService:
    def __init__(
        self,
        report_repository: FunctionalReportRepository,
        details_repository: StudentDetailsRepository,
        user_repository: UserRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._reports = report_repository
        self._details = details_repository
        self._users = user_repository
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

    def history(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> FunctionalReportHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, self._reports.list_for_student(student_id))

    def entry_history(
        self, student_id: uuid.UUID, entry_id: uuid.UUID, scope: StudentAccessScope
    ) -> FunctionalReportHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, [self._require_entry(student_id, entry_id)])

    def create(
        self,
        student_id: uuid.UUID,
        request: FunctionalReportCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> FunctionalReportEntryResponse:
        self._guard.require(student_id, scope)
        entry = FunctionalReportEntry(
            student_id=student_id, report_date=request.report_date, author_id=author_id
        )
        self._apply_sections(entry, request)
        self._reports.add(entry)
        self._record(author_id, AuditAction.CREATE, entry.id, ["report_date", *self._sections()])
        return self._to_response(entry)

    def update(
        self,
        student_id: uuid.UUID,
        entry_id: uuid.UUID,
        request: FunctionalReportUpdateRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> FunctionalReportEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        self._apply_sections(entry, request)
        self._reports.flush()
        self._record(actor_id, AuditAction.UPDATE, entry.id, list(self._sections()))
        return self._to_response(entry)

    def archive(
        self,
        student_id: uuid.UUID,
        entry_id: uuid.UUID,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> FunctionalReportEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        entry.is_archived = True
        entry.archived_at = self._clock.now()
        entry.archived_by = actor_id
        self._reports.flush()
        self._record(actor_id, AuditAction.ARCHIVE, entry.id, ["is_archived"])
        return self._to_response(entry)

    def _sections(self) -> tuple[str, ...]:
        return FunctionalReportSections.section_names()

    def _apply_sections(
        self, entry: FunctionalReportEntry, sections: FunctionalReportSections
    ) -> None:
        for name in self._sections():
            setattr(entry, name, getattr(sections, name))

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

    def _require_entry(self, student_id: uuid.UUID, entry_id: uuid.UUID) -> FunctionalReportEntry:
        entry = self._reports.get(entry_id)
        if entry is None or entry.student_id != student_id or entry.is_archived:
            raise NotFoundError("functional_report")
        return entry

    def _build_history(
        self, student: Student, entries: list[FunctionalReportEntry]
    ) -> FunctionalReportHistoryResponse:
        details = self._details.get(student.id)
        author_names: dict[uuid.UUID, str | None] = {}
        return FunctionalReportHistoryResponse(
            student_id=student.id,
            student_name=student.full_name,
            national_id=details.national_id if details is not None else None,
            date_of_birth=details.date_of_birth if details is not None else None,
            entries=[self._to_response(entry, author_names) for entry in entries],
        )

    def _to_response(
        self,
        entry: FunctionalReportEntry,
        author_names: dict[uuid.UUID, str | None] | None = None,
    ) -> FunctionalReportEntryResponse:
        return FunctionalReportEntryResponse(
            id=entry.id,
            student_id=entry.student_id,
            report_date=entry.report_date,
            author_id=entry.author_id,
            author_name=self._author_name(entry.author_id, author_names),
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            **{name: getattr(entry, name) for name in self._sections()},
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
