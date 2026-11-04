import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.routes.pdf import BrandDep, Issue, RendererDep
from backend.app.routes.security import CurrentUser, ManagerOrInstructor, require_tenant
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.schema.routes.program_upsert_request import ProgramUpsertRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.program.foci_document import FociDocument
from backend.app.service.program.program_service import ProgramService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.taxonomy.skill_focus_resolver import SkillFocusResolver
from backend.app.utils.routes.pdf_disposition import pdf_content_disposition


def get_program_service(
    session: Annotated[Session, Depends(get_session)],
) -> ProgramService:
    return ProgramService(
        ProgramRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        SkillFocusResolver(TaxonomyRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[ProgramService, Depends(get_program_service)]

router = APIRouter(
    prefix="/students/{student_id}/program",
    tags=["program"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=ProgramResponse)
def get_program(student_id: uuid.UUID, service: ServiceDep, user: CurrentUser) -> ProgramResponse:
    return service.get_for_student(student_id, StudentAccessPolicy.scope_for(user))


@router.put("", response_model=ProgramResponse)
def upsert_program(
    student_id: uuid.UUID,
    request: ProgramUpsertRequest,
    service: ServiceDep,
    writer: ManagerOrInstructor,
) -> ProgramResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.upsert(student_id, request, scope, writer.id)


@router.get("/pdf")
def get_program_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    issue: Issue,
    renderer: RendererDep,
    brand: BrandDep,
) -> Response:
    program = service.get_for_student(student_id, StudentAccessPolicy.scope_for(user))
    html = FociDocument(brand).to_html(program, issue)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": pdf_content_disposition(
                issue.student_name, "מוקדי כוח ומוקדים לחיזוק"
            )
        },
    )
