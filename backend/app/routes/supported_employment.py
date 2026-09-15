import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.supported_employment_repository import (
    SupportedEmploymentRepository,
)
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.pdf import BrandDep, RendererDep
from backend.app.routes.security import Manager, Tenant, require_tenant
from backend.app.schema.routes.supported_employment_response import SupportedEmploymentResponse
from backend.app.schema.routes.supported_employment_upsert_request import (
    SupportedEmploymentUpsertRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.supported_employment_document import SupportedEmploymentDocument
from backend.app.service.reports.supported_employment_service import SupportedEmploymentService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.service.clock import Clock


def get_supported_employment_service(
    session: Annotated[Session, Depends(get_session)],
) -> SupportedEmploymentService:
    return SupportedEmploymentService(
        SupportedEmploymentRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[SupportedEmploymentService, Depends(get_supported_employment_service)]

router = APIRouter(
    prefix="/students/{student_id}/supported-employment",
    tags=["supported-employment"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=SupportedEmploymentResponse)
def get_supported_employment(
    student_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> SupportedEmploymentResponse:
    return service.get(student_id, StudentAccessPolicy.scope_for(manager))


@router.put("", response_model=SupportedEmploymentResponse)
def upsert_supported_employment(
    student_id: uuid.UUID,
    request: SupportedEmploymentUpsertRequest,
    service: ServiceDep,
    manager: Manager,
) -> SupportedEmploymentResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)


@router.get("/pdf")
def get_supported_employment_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
    renderer: RendererDep,
    brand: BrandDep,
    tenant: Tenant,
) -> Response:
    report = service.get(student_id, StudentAccessPolicy.scope_for(manager))
    html = SupportedEmploymentDocument(brand).to_html(report, tenant.institution_name)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="supported-employment-{student_id}.pdf"'
        },
    )
