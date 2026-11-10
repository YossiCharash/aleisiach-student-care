import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import Manager, require_tenant
from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields
from backend.app.schema.routes.medical_summary_response import MedicalSummaryResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.medical_summary_document import TITLE, MedicalSummaryDocument
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


@router.get("", response_model=MedicalSummaryResponse)
def get_medical_summary(
    student_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> MedicalSummaryResponse:
    return service.get(student_id, StudentAccessPolicy.scope_for(manager))


@router.put("", response_model=MedicalSummaryResponse)
def upsert_medical_summary(
    student_id: uuid.UUID,
    request: MedicalSummaryFields,
    service: ServiceDep,
    manager: Manager,
) -> MedicalSummaryResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)


@router.get("/pdf")
def get_medical_summary_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    summary = service.get(student_id, StudentAccessPolicy.scope_for(manager))
    html = MedicalSummaryDocument(brand).to_html(summary, issue)
    return Response(
        content=renderer.render(html),
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(issue.student_name, TITLE)},
    )
