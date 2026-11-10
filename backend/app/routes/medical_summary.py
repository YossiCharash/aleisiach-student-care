import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import Manager, require_tenant
from backend.app.schema.routes.medical_summary_create_request import MedicalSummaryCreateRequest
from backend.app.schema.routes.medical_summary_entry_response import MedicalSummaryEntryResponse
from backend.app.schema.routes.medical_summary_history_response import (
    MedicalSummaryHistoryResponse,
)
from backend.app.schema.routes.medical_summary_request import MedicalSummaryRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.medical_summary_document import (
    COMBINED_TITLE,
    TITLE,
    MedicalSummaryDocument,
)
from backend.app.service.reports.medical_summary_service import MedicalSummaryService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition
from backend.app.utils.service.clock import Clock


def get_medical_summary_service(
    session: Annotated[Session, Depends(get_session)],
) -> MedicalSummaryService:
    return MedicalSummaryService(
        MedicalSummaryRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[MedicalSummaryService, Depends(get_medical_summary_service)]

router = APIRouter(
    prefix="/students/{student_id}/medical-summary",
    tags=["medical-summary"],
    dependencies=[Depends(require_tenant)],
)


def _pdf_response(pdf: bytes, student_name: str, document_name: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(student_name, document_name)},
    )


@router.get("", response_model=MedicalSummaryHistoryResponse)
def list_medical_summaries(
    student_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> MedicalSummaryHistoryResponse:
    return service.history(student_id, StudentAccessPolicy.scope_for(manager))


@router.post("", response_model=MedicalSummaryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_medical_summary(
    student_id: uuid.UUID,
    request: MedicalSummaryCreateRequest,
    service: ServiceDep,
    manager: Manager,
) -> MedicalSummaryEntryResponse:
    return service.create(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)


@router.put("/{entry_id}", response_model=MedicalSummaryEntryResponse)
def update_medical_summary(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    request: MedicalSummaryRequest,
    service: ServiceDep,
    manager: Manager,
) -> MedicalSummaryEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.update(student_id, entry_id, request, scope, manager.id)


@router.post("/{entry_id}/archive", response_model=MedicalSummaryEntryResponse)
def archive_medical_summary(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
) -> MedicalSummaryEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.archive(student_id, entry_id, scope, manager.id)


@router.get("/pdf")
def get_medical_summaries_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    history = service.history(student_id, StudentAccessPolicy.scope_for(manager))
    pdf = renderer.render(MedicalSummaryDocument(brand).combined_html(history, issue))
    return _pdf_response(pdf, issue.student_name, COMBINED_TITLE)


@router.get("/{entry_id}/pdf")
def get_medical_summary_pdf(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    scope = StudentAccessPolicy.scope_for(manager)
    history = service.entry_history(student_id, entry_id, scope)
    pdf = renderer.render(MedicalSummaryDocument(brand).single_html(history, issue))
    return _pdf_response(pdf, issue.student_name, TITLE)
