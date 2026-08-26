import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.security import Manager, SocialNoteReader
from backend.app.schema.routes.social_note_response import SocialNoteResponse
from backend.app.schema.routes.social_note_upsert_request import SocialNoteUpsertRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.notes.social_note_service import SocialNoteService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.service.clock import Clock


def get_social_note_service(
    session: Annotated[Session, Depends(get_session)],
) -> SocialNoteService:
    return SocialNoteService(
        SocialNoteRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[SocialNoteService, Depends(get_social_note_service)]

router = APIRouter(prefix="/students/{student_id}/social-note", tags=["social-note"])


@router.get("", response_model=SocialNoteResponse)
def get_social_note(
    student_id: uuid.UUID, service: ServiceDep, reader: SocialNoteReader
) -> SocialNoteResponse:
    return service.get(student_id, StudentAccessPolicy.scope_for(reader))


@router.put("", response_model=SocialNoteResponse)
def upsert_social_note(
    student_id: uuid.UUID,
    request: SocialNoteUpsertRequest,
    service: ServiceDep,
    manager: Manager,
) -> SocialNoteResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(manager), manager.id)
