import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.schema.routes.program_upsert_request import ProgramUpsertRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.program.program_service import ProgramService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.taxonomy.skill_rating_resolver import SkillRatingResolver


def get_program_service(
    session: Annotated[Session, Depends(get_session)],
) -> ProgramService:
    return ProgramService(
        ProgramRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        SkillRatingResolver(TaxonomyRepository(session)),
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
    writer: Manager,
) -> ProgramResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.upsert(student_id, request, scope, writer.id)
