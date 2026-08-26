import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.database.provider import get_session
from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.routes.security import CurrentUser, MeetingWriter
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.service.meetings.meeting_service import MeetingService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy


def get_meeting_service(
    session: Annotated[Session, Depends(get_session)],
) -> MeetingService:
    return MeetingService(
        MeetingRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        TaxonomyRepository(session),
    )


ServiceDep = Annotated[MeetingService, Depends(get_meeting_service)]

router = APIRouter(prefix="/students/{student_id}/meetings", tags=["meetings"])


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    student_id: uuid.UUID,
    request: MeetingCreateRequest,
    service: ServiceDep,
    writer: MeetingWriter,
) -> MeetingResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.create(student_id, request, scope, writer.id)


@router.get("", response_model=list[MeetingResponse])
def list_meetings(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> list[MeetingResponse]:
    return service.list_for_student(student_id, StudentAccessPolicy.scope_for(user))


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    student_id: uuid.UUID,
    meeting_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
) -> MeetingResponse:
    return service.get(student_id, meeting_id, StudentAccessPolicy.scope_for(user))
