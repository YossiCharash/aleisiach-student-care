import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.incident_report_repository import IncidentReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import CurrentUser, Manager, ManagerOrInstructor, require_tenant
from backend.app.schema.routes.incident_report_entry_response import IncidentReportEntryResponse
from backend.app.schema.routes.incident_report_history_response import (
    IncidentReportHistoryResponse,
)
from backend.app.schema.routes.incident_report_request import IncidentReportRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.incident_report_document import IncidentReportDocument
from backend.app.service.reports.incident_report_service import IncidentReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition
from backend.app.utils.service.clock import Clock


def get_incident_report_service(
    session: Annotated[Session, Depends(get_session)],
) -> IncidentReportService:
    return IncidentReportService(
        IncidentReportRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[IncidentReportService, Depends(get_incident_report_service)]

router = APIRouter(
    prefix="/students/{student_id}/incident-reports",
    tags=["incident-reports"],
    dependencies=[Depends(require_tenant)],
)


def _pdf_response(pdf: bytes, student_name: str, document_name: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(student_name, document_name)},
    )


@router.get("", response_model=IncidentReportHistoryResponse)
def list_incident_reports(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> IncidentReportHistoryResponse:
    return service.history(student_id, StudentAccessPolicy.scope_for(user))


@router.post("", response_model=IncidentReportEntryResponse, status_code=status.HTTP_201_CREATED)
def create_incident_report(
    student_id: uuid.UUID,
    request: IncidentReportRequest,
    service: ServiceDep,
    writer: ManagerOrInstructor,
) -> IncidentReportEntryResponse:
    return service.create(student_id, request, StudentAccessPolicy.scope_for(writer), writer.id)


@router.put("/{report_id}", response_model=IncidentReportEntryResponse)
def update_incident_report(
    student_id: uuid.UUID,
    report_id: uuid.UUID,
    request: IncidentReportRequest,
    service: ServiceDep,
    writer: ManagerOrInstructor,
) -> IncidentReportEntryResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.update(student_id, report_id, request, scope, writer.id)


@router.post("/{report_id}/archive", response_model=IncidentReportEntryResponse)
def archive_incident_report(
    student_id: uuid.UUID,
    report_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
) -> IncidentReportEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.archive(student_id, report_id, scope, manager.id)


@router.get("/pdf")
def get_incident_reports_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    history = service.history(student_id, StudentAccessPolicy.scope_for(user))
    pdf = renderer.render(IncidentReportDocument(brand).combined_html(history, issue))
    return _pdf_response(pdf, issue.student_name, "דוחות אירוע חריג")


@router.get("/{report_id}/pdf")
def get_incident_report_pdf(
    student_id: uuid.UUID,
    report_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    history = service.entry_history(student_id, report_id, StudentAccessPolicy.scope_for(user))
    pdf = renderer.render(IncidentReportDocument(brand).single_html(history, issue))
    return _pdf_response(pdf, issue.student_name, "דוח אירוע חריג")
