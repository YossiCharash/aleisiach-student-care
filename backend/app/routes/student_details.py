import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.diagnosis_catalog_repository import (
    DiagnosisCatalogRepository,
)
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.pdf import RendererDep
from backend.app.routes.security import ContentWriter, CurrentUser
from backend.app.schema.routes.student_details_response import StudentDetailsResponse
from backend.app.schema.routes.student_details_upsert_request import (
    StudentDetailsUpsertRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.diagnosis_catalog_service import DiagnosisCatalogService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.students.student_details_document import StudentDetailsDocument
from backend.app.service.students.student_details_service import StudentDetailsService
from backend.app.utils.service.clock import Clock


def get_student_details_service(
    session: Annotated[Session, Depends(get_session)],
) -> StudentDetailsService:
    audit_logger = AuditLogger(AuditLogRepository(session))
    return StudentDetailsService(
        StudentDetailsRepository(session),
        DiagnosisCatalogService(DiagnosisCatalogRepository(session), audit_logger),
        StudentAccessGuard(StudentRepository(session)),
        audit_logger,
        Clock(),
    )


ServiceDep = Annotated[StudentDetailsService, Depends(get_student_details_service)]

router = APIRouter(prefix="/students/{student_id}/details", tags=["student-details"])


@router.get("", response_model=StudentDetailsResponse)
def get_details(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> StudentDetailsResponse:
    return service.get(
        student_id,
        StudentAccessPolicy.scope_for(user),
        StudentAccessPolicy.can_see_sensitive(user),
    )


@router.put("", response_model=StudentDetailsResponse)
def upsert_details(
    student_id: uuid.UUID,
    request: StudentDetailsUpsertRequest,
    service: ServiceDep,
    writer: ContentWriter,
) -> StudentDetailsResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(writer), writer.id)


@router.get("/pdf")
def get_details_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    renderer: RendererDep,
) -> Response:
    details = service.get(
        student_id,
        StudentAccessPolicy.scope_for(user),
        StudentAccessPolicy.can_see_sensitive(user),
    )
    pdf = renderer.render(StudentDetailsDocument().to_html(details))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="details-{student_id}.pdf"'},
    )
