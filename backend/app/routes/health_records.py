import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.health_domain_repository import HealthDomainRepository
from backend.app.client.reports.health_record_repository import HealthRecordRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.health_record_history_response import (
    HealthRecordHistoryResponse,
)
from backend.app.schema.routes.health_record_request import HealthRecordRequest
from backend.app.schema.routes.health_record_response import HealthRecordResponse
from backend.app.schema.routes.staff_member_response import StaffMemberResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.health_record_document import TITLE, HealthRecordDocument
from backend.app.service.reports.health_record_service import HealthRecordService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition
from backend.app.utils.service.clock import Clock


def get_health_record_service(
    session: Annotated[Session, Depends(get_session)],
) -> HealthRecordService:
    return HealthRecordService(
        HealthRecordRepository(session),
        HealthDomainRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[HealthRecordService, Depends(get_health_record_service)]

router = APIRouter(
    prefix="/students/{student_id}/health-records",
    tags=["health-records"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=HealthRecordHistoryResponse)
def list_health_records(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> HealthRecordHistoryResponse:
    return service.history(student_id, StudentAccessPolicy.scope_for(user))


@router.get("/responsible-candidates", response_model=list[StaffMemberResponse])
def list_responsible_candidates(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> list[StaffMemberResponse]:
    return service.responsible_candidates(student_id, StudentAccessPolicy.scope_for(user))


@router.post("", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
def create_health_record(
    student_id: uuid.UUID,
    request: HealthRecordRequest,
    service: ServiceDep,
    user: CurrentUser,
) -> HealthRecordResponse:
    return service.create(student_id, request, StudentAccessPolicy.scope_for(user), user.id)


@router.put("/{record_id}", response_model=HealthRecordResponse)
def update_health_record(
    student_id: uuid.UUID,
    record_id: uuid.UUID,
    request: HealthRecordRequest,
    service: ServiceDep,
    user: CurrentUser,
) -> HealthRecordResponse:
    scope = StudentAccessPolicy.scope_for(user)
    return service.update(student_id, record_id, request, scope, user.id)


@router.post("/{record_id}/archive", response_model=HealthRecordResponse)
def archive_health_record(
    student_id: uuid.UUID,
    record_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
) -> HealthRecordResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.archive(student_id, record_id, scope, manager.id)


@router.get("/pdf")
def get_health_records_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
    domain_id: uuid.UUID | None = None,
) -> Response:
    history = service.history(student_id, StudentAccessPolicy.scope_for(user), domain_id)
    pdf = renderer.render(HealthRecordDocument(brand).html(history, issue))
    document_name = TITLE
    if domain_id is not None and history.domains:
        document_name = f"{TITLE} - {history.domains[0].name}"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(issue.student_name, document_name)},
    )
