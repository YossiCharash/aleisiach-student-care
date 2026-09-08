import uuid

from backend.app.client.reports.functional_report_repository import FunctionalReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.functional_report import FunctionalReport
from backend.app.models.client.student import Student
from backend.app.schema.routes.functional_report_response import FunctionalReportResponse
from backend.app.schema.routes.functional_report_upsert_request import (
    FunctionalReportUpsertRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "functional_report"
_SECTIONS = (
    "general_background",
    "vocational_domain",
    "behavioral_emotional_domain",
    "communication_social_domain",
    "independence_life_skills_domain",
    "summary_recommendations",
)


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

    def get(self, student_id: uuid.UUID, scope: StudentAccessScope) -> FunctionalReportResponse:
        student = self._guard.require(student_id, scope)
        report = self._reports.get(student_id)
        return self._to_response(student, report)

    def upsert(
        self,
        student_id: uuid.UUID,
        request: FunctionalReportUpsertRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> FunctionalReportResponse:
        student = self._guard.require(student_id, scope)
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
                changes=list(_SECTIONS),
            )
        )
        return self._to_response(student, report)

    def _build(
        self, student_id: uuid.UUID, request: FunctionalReportUpsertRequest, actor_id: uuid.UUID
    ) -> FunctionalReport:
        report = FunctionalReport(student_id=student_id)
        self._apply(report, request, actor_id)
        return report

    def _apply(
        self, report: FunctionalReport, request: FunctionalReportUpsertRequest, actor_id: uuid.UUID
    ) -> None:
        for section in _SECTIONS:
            setattr(report, section, getattr(request, section))
        report.updated_by = actor_id
        report.updated_at = self._clock.now()

    def _to_response(
        self, student: Student, report: FunctionalReport | None
    ) -> FunctionalReportResponse:
        details = self._details.get(student.id)
        national_id = details.national_id if details is not None else None
        date_of_birth = details.date_of_birth if details is not None else None
        if report is None:
            return FunctionalReportResponse(
                student_id=student.id,
                exists=False,
                student_name=student.full_name,
                national_id=national_id,
                date_of_birth=date_of_birth,
            )
        writer = self._users.get(report.updated_by)
        return FunctionalReportResponse(
            student_id=student.id,
            exists=True,
            student_name=student.full_name,
            national_id=national_id,
            date_of_birth=date_of_birth,
            general_background=report.general_background,
            vocational_domain=report.vocational_domain,
            behavioral_emotional_domain=report.behavioral_emotional_domain,
            communication_social_domain=report.communication_social_domain,
            independence_life_skills_domain=report.independence_life_skills_domain,
            summary_recommendations=report.summary_recommendations,
            written_by_name=writer.full_name if writer is not None else None,
            updated_at=report.updated_at,
        )
