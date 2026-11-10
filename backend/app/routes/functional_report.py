import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.functional_report_repository import FunctionalReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.functional_report_create_request import (
    FunctionalReportCreateRequest,
)
from backend.app.schema.routes.functional_report_entry_response import (
    FunctionalReportEntryResponse,
)
from backend.app.schema.routes.functional_report_history_response import (
    FunctionalReportHistoryResponse,
)
from backend.app.schema.routes.functional_report_update_request import (
    FunctionalReportUpdateRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.functional_report_document import FunctionalReportDocument
from backend.app.service.reports.functional_report_service import FunctionalReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition
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


def _pdf_response(pdf: bytes, student_name: str, document_name: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(student_name, document_name)},
    )


@router.get("", response_model=FunctionalReportHistoryResponse)
def list_functional_reports(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> FunctionalReportHistoryResponse:
    return service.history(student_id, StudentAccessPolicy.scope_for(user))


@router.post("", response_model=FunctionalReportEntryResponse, status_code=status.HTTP_201_CREATED)
def create_functional_report(
    student_id: uuid.UUID,
    request: FunctionalReportCreateRequest,
    service: ServiceDep,
    manager: Manager,
) -> FunctionalReportEntryResponse:
    return service.create(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)


@router.patch("/{entry_id}", response_model=FunctionalReportEntryResponse)
def update_functional_report(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    request: FunctionalReportUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> FunctionalReportEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.update(student_id, entry_id, request, scope, manager.id)


@router.post("/{entry_id}/archive", response_model=FunctionalReportEntryResponse)
def archive_functional_report(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
) -> FunctionalReportEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.archive(student_id, entry_id, scope, manager.id)


@router.get("/pdf")
def get_functional_reports_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    history = service.history(student_id, StudentAccessPolicy.scope_for(user))
    pdf = renderer.render(FunctionalReportDocument(brand).combined_html(history, issue))
    return _pdf_response(pdf, issue.student_name, "דוחות תפקודיים")


@router.get("/{entry_id}/pdf")
def get_functional_report_pdf(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    history = service.entry_history(student_id, entry_id, StudentAccessPolicy.scope_for(user))
    pdf = renderer.render(FunctionalReportDocument(brand).single_html(history, issue))
    return _pdf_response(pdf, issue.student_name, "דוח תפקודי")
