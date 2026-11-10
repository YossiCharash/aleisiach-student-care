import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.risk_assessment_repository import RiskAssessmentRepository
from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import CurrentUser, Manager, ManagerOrInstructor, require_tenant
from backend.app.schema.routes.risk_assessment_entry_response import RiskAssessmentEntryResponse
from backend.app.schema.routes.risk_assessment_history_response import (
    RiskAssessmentHistoryResponse,
)
from backend.app.schema.routes.risk_assessment_request import RiskAssessmentRequest
from backend.app.schema.routes.staff_member_response import StaffMemberResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.risk_assessment_document import RiskAssessmentDocument
from backend.app.service.reports.risk_assessment_service import RiskAssessmentService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition
from backend.app.utils.service.clock import Clock


def get_risk_assessment_service(
    session: Annotated[Session, Depends(get_session)],
) -> RiskAssessmentService:
    return RiskAssessmentService(
        RiskAssessmentRepository(session),
        RiskDomainRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[RiskAssessmentService, Depends(get_risk_assessment_service)]

router = APIRouter(
    prefix="/students/{student_id}/risk-assessments",
    tags=["risk-assessments"],
    dependencies=[Depends(require_tenant)],
)


def _pdf_response(pdf: bytes, student_name: str, document_name: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": pdf_content_disposition(student_name, document_name)},
    )


@router.get("", response_model=RiskAssessmentHistoryResponse)
def list_risk_assessments(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> RiskAssessmentHistoryResponse:
    return service.history(student_id, StudentAccessPolicy.scope_for(user))


@router.get("/responsible-candidates", response_model=list[StaffMemberResponse])
def list_responsible_candidates(
    student_id: uuid.UUID, service: ServiceDep, writer: ManagerOrInstructor
) -> list[StaffMemberResponse]:
    return service.responsible_candidates(student_id, StudentAccessPolicy.scope_for(writer))


@router.post("", response_model=RiskAssessmentEntryResponse, status_code=status.HTTP_201_CREATED)
def create_risk_assessment(
    student_id: uuid.UUID,
    request: RiskAssessmentRequest,
    service: ServiceDep,
    writer: ManagerOrInstructor,
) -> RiskAssessmentEntryResponse:
    return service.create(student_id, request, StudentAccessPolicy.scope_for(writer), writer.id)


@router.put("/{assessment_id}", response_model=RiskAssessmentEntryResponse)
def update_risk_assessment(
    student_id: uuid.UUID,
    assessment_id: uuid.UUID,
    request: RiskAssessmentRequest,
    service: ServiceDep,
    writer: ManagerOrInstructor,
) -> RiskAssessmentEntryResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.update(student_id, assessment_id, request, scope, writer.id)


@router.post("/{assessment_id}/archive", response_model=RiskAssessmentEntryResponse)
def archive_risk_assessment(
    student_id: uuid.UUID,
    assessment_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
) -> RiskAssessmentEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.archive(student_id, assessment_id, scope, manager.id)


@router.get("/pdf")
def get_risk_assessments_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    history = service.history(student_id, StudentAccessPolicy.scope_for(user))
    pdf = renderer.render(RiskAssessmentDocument(brand).combined_html(history, issue))
    return _pdf_response(pdf, issue.student_name, "טבלאות ניהול סיכונים")


@router.get("/{assessment_id}/pdf")
def get_risk_assessment_pdf(
    student_id: uuid.UUID,
    assessment_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    scope = StudentAccessPolicy.scope_for(user)
    history = service.entry_history(student_id, assessment_id, scope)
    pdf = renderer.render(RiskAssessmentDocument(brand).single_html(history, issue))
    return _pdf_response(pdf, issue.student_name, "ניהול סיכונים")
