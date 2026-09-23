import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.reception_report_repository import ReceptionReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import Manager, require_tenant
from backend.app.schema.routes.reception_report_response import ReceptionReportResponse
from backend.app.schema.routes.reception_report_upsert_request import (
    ReceptionReportUpsertRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.reception_report_document import ReceptionReportDocument
from backend.app.service.reports.reception_report_service import ReceptionReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition
from backend.app.utils.service.clock import Clock


def get_reception_report_service(
    session: Annotated[Session, Depends(get_session)],
) -> ReceptionReportService:
    return ReceptionReportService(
        ReceptionReportRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[ReceptionReportService, Depends(get_reception_report_service)]

router = APIRouter(
    prefix="/students/{student_id}/reception-report",
    tags=["reception-report"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=ReceptionReportResponse)
def get_reception_report(
    student_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> ReceptionReportResponse:
    return service.get(student_id, StudentAccessPolicy.scope_for(manager))


@router.put("", response_model=ReceptionReportResponse)
def upsert_reception_report(
    student_id: uuid.UUID,
    request: ReceptionReportUpsertRequest,
    service: ServiceDep,
    manager: Manager,
) -> ReceptionReportResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)


@router.get("/pdf")
def get_reception_report_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    report = service.get(student_id, StudentAccessPolicy.scope_for(manager))
    html = ReceptionReportDocument(brand).to_html(report, issue)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(issue.student_name, "דוח קבלה")},
    )
