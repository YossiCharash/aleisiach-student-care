import uuid

from backend.app.client.reports.reception_report_repository import ReceptionReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.reception_report import ReceptionReport
from backend.app.models.client.student import Student
from backend.app.schema.routes.reception_checklist_item import ReceptionChecklistItem
from backend.app.schema.routes.reception_report_response import ReceptionReportResponse
from backend.app.schema.routes.reception_report_upsert_request import (
    ReceptionReportUpsertRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "reception_report"
_SCALAR_FIELDS = (
    "committee_date",
    "committee_participants",
    "intake_date",
    "committee_summary",
    "committee_recommendations",
    "framework_code",
    "tariff_code",
)
_CHECKLIST_FIELDS = (
    "committee_held",
    "director_approval",
    "family_guardian_housing_updated",
    "community_social_worker_updated",
    "management_updated",
)


class ReceptionReportService:
    def __init__(
        self,
        report_repository: ReceptionReportRepository,
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

    def get(self, student_id: uuid.UUID, scope: StudentAccessScope) -> ReceptionReportResponse:
        student = self._guard.require(student_id, scope)
        report = self._reports.get(student_id)
        return self._to_response(student, report)

    def upsert(
        self,
        student_id: uuid.UUID,
        request: ReceptionReportUpsertRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> ReceptionReportResponse:
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
                changes=[*_SCALAR_FIELDS, *_CHECKLIST_FIELDS],
            )
        )
        return self._to_response(student, report)

    def _build(
        self, student_id: uuid.UUID, request: ReceptionReportUpsertRequest, actor_id: uuid.UUID
    ) -> ReceptionReport:
        report = ReceptionReport(student_id=student_id)
        self._apply(report, request, actor_id)
        return report

    def _apply(
        self, report: ReceptionReport, request: ReceptionReportUpsertRequest, actor_id: uuid.UUID
    ) -> None:
        for field in _SCALAR_FIELDS:
            setattr(report, field, getattr(request, field))
        for field in _CHECKLIST_FIELDS:
            item: ReceptionChecklistItem = getattr(request, field)
            setattr(report, field, item.done)
            setattr(report, f"{field}_note", item.note)
        report.updated_by = actor_id
        report.updated_at = self._clock.now()

    def _to_response(
        self, student: Student, report: ReceptionReport | None
    ) -> ReceptionReportResponse:
        details = self._details.get(student.id)
        national_id = details.national_id if details is not None else None
        date_of_birth = details.date_of_birth if details is not None else None
        if report is None:
            return ReceptionReportResponse(
                student_id=student.id,
                exists=False,
                student_name=student.full_name,
                national_id=national_id,
                date_of_birth=date_of_birth,
            )
        writer = self._users.get(report.updated_by)
        return ReceptionReportResponse(
            student_id=student.id,
            exists=True,
            student_name=student.full_name,
            national_id=national_id,
            date_of_birth=date_of_birth,
            committee_date=report.committee_date,
            committee_participants=report.committee_participants,
            intake_date=report.intake_date,
            committee_summary=report.committee_summary,
            committee_recommendations=report.committee_recommendations,
            framework_code=report.framework_code,
            tariff_code=report.tariff_code,
            committee_held=self._item(report, "committee_held"),
            director_approval=self._item(report, "director_approval"),
            family_guardian_housing_updated=self._item(report, "family_guardian_housing_updated"),
            community_social_worker_updated=self._item(report, "community_social_worker_updated"),
            management_updated=self._item(report, "management_updated"),
            written_by_name=writer.full_name if writer is not None else None,
            updated_at=report.updated_at,
        )

    def _item(self, report: ReceptionReport, field: str) -> ReceptionChecklistItem:
        return ReceptionChecklistItem(
            done=getattr(report, field), note=getattr(report, f"{field}_note")
        )
