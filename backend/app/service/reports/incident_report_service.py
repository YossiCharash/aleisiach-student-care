import uuid

from backend.app.client.reports.incident_report_repository import IncidentReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.incident_report import IncidentReport
from backend.app.models.client.student import Student
from backend.app.schema.routes.incident_report_entry_response import IncidentReportEntryResponse
from backend.app.schema.routes.incident_report_fields import IncidentReportFields
from backend.app.schema.routes.incident_report_history_response import (
    IncidentReportHistoryResponse,
)
from backend.app.schema.routes.incident_report_request import IncidentReportRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "incident_report"


class IncidentReportService:
    def __init__(
        self,
        report_repository: IncidentReportRepository,
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
    ) -> IncidentReportHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, self._reports.list_for_student(student_id))

    def entry_history(
        self, student_id: uuid.UUID, report_id: uuid.UUID, scope: StudentAccessScope
    ) -> IncidentReportHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, [self._require_report(student_id, report_id)])

    def create(
        self,
        student_id: uuid.UUID,
        request: IncidentReportRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> IncidentReportEntryResponse:
        self._guard.require(student_id, scope)
        report = IncidentReport(student_id=student_id, author_id=author_id)
        self._apply_fields(report, request)
        self._reports.add(report)
        self._record(author_id, AuditAction.CREATE, report.id, list(self._fields()))
        return self._to_response(report)

    def update(
        self,
        student_id: uuid.UUID,
        report_id: uuid.UUID,
        request: IncidentReportRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> IncidentReportEntryResponse:
        self._guard.require(student_id, scope)
        report = self._require_report(student_id, report_id)
        changed = [
            name for name in self._fields() if getattr(report, name) != getattr(request, name)
        ]
        self._apply_fields(report, request)
        self._reports.flush()
        self._record(actor_id, AuditAction.UPDATE, report.id, changed)
        return self._to_response(report)

    def archive(
        self,
        student_id: uuid.UUID,
        report_id: uuid.UUID,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> IncidentReportEntryResponse:
        self._guard.require(student_id, scope)
        report = self._require_report(student_id, report_id)
        report.is_archived = True
        report.archived_at = self._clock.now()
        report.archived_by = actor_id
        self._reports.flush()
        self._record(actor_id, AuditAction.ARCHIVE, report.id, ["is_archived"])
        return self._to_response(report)

    def _fields(self) -> tuple[str, ...]:
        return IncidentReportFields.field_names()

    def _apply_fields(self, report: IncidentReport, fields: IncidentReportFields) -> None:
        for name in self._fields():
            setattr(report, name, getattr(fields, name))

    def _record(
        self, actor_id: uuid.UUID, action: AuditAction, report_id: uuid.UUID, changes: list[str]
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=report_id,
                changes=changes,
            )
        )

    def _require_report(self, student_id: uuid.UUID, report_id: uuid.UUID) -> IncidentReport:
        report = self._reports.get(report_id)
        if report is None or report.student_id != student_id or report.is_archived:
            raise NotFoundError("incident_report")
        return report

    def _build_history(
        self, student: Student, reports: list[IncidentReport]
    ) -> IncidentReportHistoryResponse:
        details = self._details.get(student.id)
        author_names: dict[uuid.UUID, str | None] = {}
        return IncidentReportHistoryResponse(
            student_id=student.id,
            student_name=student.full_name,
            national_id=details.national_id if details is not None else None,
            entries=[self._to_response(report, author_names) for report in reports],
        )

    def _to_response(
        self,
        report: IncidentReport,
        author_names: dict[uuid.UUID, str | None] | None = None,
    ) -> IncidentReportEntryResponse:
        return IncidentReportEntryResponse(
            id=report.id,
            student_id=report.student_id,
            author_id=report.author_id,
            author_name=self._author_name(report.author_id, author_names),
            created_at=report.created_at,
            updated_at=report.updated_at,
            **{name: getattr(report, name) for name in self._fields()},
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
