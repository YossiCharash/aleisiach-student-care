import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.program.program_plan_repository import ProgramPlanRepository
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.routes.pdf import BrandDep, RendererDep
from backend.app.routes.security import CurrentUser, ManagerOrInstructor, Tenant, require_tenant
from backend.app.schema.routes.plan_create_request import PlanCreateRequest
from backend.app.schema.routes.plan_response import PlanResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.program.plan_document import PlanDocument
from backend.app.service.program.program_plan_service import ProgramPlanService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy


def get_program_plan_service(
    session: Annotated[Session, Depends(get_session)],
) -> ProgramPlanService:
    return ProgramPlanService(
        ProgramPlanRepository(session),
        ProgramRepository(session),
        TaxonomyRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[ProgramPlanService, Depends(get_program_plan_service)]

router = APIRouter(
    prefix="/students/{student_id}/program/plans",
    tags=["program-plans"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=list[PlanResponse])
def list_plans(student_id: uuid.UUID, service: ServiceDep, user: CurrentUser) -> list[PlanResponse]:
    return service.list_for_student(student_id, StudentAccessPolicy.scope_for(user))


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    student_id: uuid.UUID,
    request: PlanCreateRequest,
    service: ServiceDep,
    writer: ManagerOrInstructor,
) -> PlanResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.create(student_id, request, scope, writer.id)


@router.get("/pdf")
def get_plans_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    renderer: RendererDep,
    brand: BrandDep,
    tenant: Tenant,
) -> Response:
    plans = service.list_for_student(student_id, StudentAccessPolicy.scope_for(user))
    html = PlanDocument(brand).combined_html(plans, tenant.institution_name)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="plans-{student_id}.pdf"'},
    )


@router.get("/{plan_id}/pdf")
def get_plan_pdf(
    student_id: uuid.UUID,
    plan_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    renderer: RendererDep,
    brand: BrandDep,
    tenant: Tenant,
) -> Response:
    plan = service.get(student_id, plan_id, StudentAccessPolicy.scope_for(user))
    html = PlanDocument(brand).to_html(plan, tenant.institution_name)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="plan-{plan_id}.pdf"'},
    )
