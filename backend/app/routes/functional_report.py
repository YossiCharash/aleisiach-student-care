import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.functional_report_repository import FunctionalReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, RendererDep
from backend.app.routes.security import CurrentUser, Manager, Tenant, require_tenant
from backend.app.schema.routes.functional_report_response import FunctionalReportResponse
from backend.app.schema.routes.functional_report_upsert_request import (
    FunctionalReportUpsertRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.functional_report_document import FunctionalReportDocument
from backend.app.service.reports.functional_report_service import FunctionalReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.service.clock import Clock


def get_functional_report_service(
    session: Annotated[Session, Depends(get_session)],
) -> FunctionalReportService:
    return FunctionalReportService(
        FunctionalReportRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[FunctionalReportService, Depends(get_functional_report_service)]

router = APIRouter(
    prefix="/students/{student_id}/functional-report",
    tags=["functional-report"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=FunctionalReportResponse)
def get_functional_report(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> FunctionalReportResponse:
    return service.get(student_id, StudentAccessPolicy.scope_for(user))


@router.put("", response_model=FunctionalReportResponse)
def upsert_functional_report(
    student_id: uuid.UUID,
    request: FunctionalReportUpsertRequest,
    service: ServiceDep,
    manager: Manager,
) -> FunctionalReportResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)


@router.get("/pdf")
def get_functional_report_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    renderer: RendererDep,
    brand: BrandDep,
    tenant: Tenant,
) -> Response:
    report = service.get(student_id, StudentAccessPolicy.scope_for(user))
    html = FunctionalReportDocument(brand).to_html(report, tenant.institution_name)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="functional-report-{student_id}.pdf"'},
    )
