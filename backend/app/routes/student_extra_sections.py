import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.extra_section_type_repository import (
    ExtraSectionTypeRepository,
)
from backend.app.client.students.student_extra_section_repository import (
    StudentExtraSectionRepository,
)
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.security import ContentWriter, CurrentUser
from backend.app.schema.routes.student_extra_section_entry import StudentExtraSectionEntry
from backend.app.schema.routes.student_extra_section_upsert_request import (
    StudentExtraSectionUpsertRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.students.student_extra_section_service import (
    StudentExtraSectionService,
)


def get_student_extra_section_service(
    session: Annotated[Session, Depends(get_session)],
) -> StudentExtraSectionService:
    return StudentExtraSectionService(
        StudentExtraSectionRepository(session),
        ExtraSectionTypeRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[StudentExtraSectionService, Depends(get_student_extra_section_service)]

router = APIRouter(prefix="/students/{student_id}/extra-sections", tags=["student-extra-sections"])


@router.get("", response_model=list[StudentExtraSectionEntry])
def get_sections(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> list[StudentExtraSectionEntry]:
    return service.get_for_student(student_id, StudentAccessPolicy.scope_for(user))


@router.put("/{section_type_id}", response_model=StudentExtraSectionEntry)
def set_section(
    student_id: uuid.UUID,
    section_type_id: uuid.UUID,
    request: StudentExtraSectionUpsertRequest,
    service: ServiceDep,
    writer: ContentWriter,
) -> StudentExtraSectionEntry:
    return service.set(
        student_id,
        section_type_id,
        request,
        StudentAccessPolicy.scope_for(writer),
        writer.id,
    )
