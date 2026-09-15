import uuid

from backend.app.client.reports.supported_employment_repository import (
    SupportedEmploymentRepository,
)
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.supported_employment import SupportedEmployment
from backend.app.schema.routes.supported_employment_response import SupportedEmploymentResponse
from backend.app.schema.routes.supported_employment_upsert_request import (
    SupportedEmploymentUpsertRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "supported_employment"
_FIELDS = (
    "workplace",
    "address",
    "activity_type",
    "work_process",
    "work_environment",
    "required_body_functions",
    "hazards_and_safety",
    "workplace_contact",
    "escort_contact",
    "mobility",
    "work_hours",
)


class SupportedEmploymentService:
    def __init__(
        self,
        report_repository: SupportedEmploymentRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._reports = report_repository
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

    def get(self, student_id: uuid.UUID, scope: StudentAccessScope) -> SupportedEmploymentResponse:
        self._guard.require(student_id, scope)
        report = self._reports.get(student_id)
        return self._to_response(student_id, report)

    def upsert(
        self,
        student_id: uuid.UUID,
        request: SupportedEmploymentUpsertRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> SupportedEmploymentResponse:
        self._guard.require(student_id, scope)
        report = self._reports.get(student_id)
        if report is None:
            report, created = self._reports.create(self._build(student_id, request, actor_id))
        else:
            created = False
        if not created:
            self._apply(report, request, actor_id)
            self._reports.flush()
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE if created else AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=student_id,
                changes=list(_FIELDS),
            )
        )
        return self._to_response(student_id, report)

    def _build(
        self,
        student_id: uuid.UUID,
        request: SupportedEmploymentUpsertRequest,
        actor_id: uuid.UUID,
    ) -> SupportedEmployment:
        report = SupportedEmployment(student_id=student_id)
        self._apply(report, request, actor_id)
        return report

    def _apply(
        self,
        report: SupportedEmployment,
        request: SupportedEmploymentUpsertRequest,
        actor_id: uuid.UUID,
    ) -> None:
        for field in _FIELDS:
            setattr(report, field, getattr(request, field))
        report.updated_by = actor_id
        report.updated_at = self._clock.now()

    def _to_response(
        self, student_id: uuid.UUID, report: SupportedEmployment | None
    ) -> SupportedEmploymentResponse:
        if report is None:
            return SupportedEmploymentResponse(student_id=student_id, exists=False)
        return SupportedEmploymentResponse(
            student_id=student_id,
            exists=True,
            **{field: getattr(report, field) for field in _FIELDS},
        )
