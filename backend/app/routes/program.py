import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.client.database.provider import get_session
from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.security import CurrentUser
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.service.program.program_service import ProgramService
from backend.app.service.students.student_access_policy import StudentAccessPolicy


def get_program_service(
    session: Annotated[Session, Depends(get_session)],
) -> ProgramService:
    return ProgramService(MeetingRepository(session), StudentRepository(session))


ServiceDep = Annotated[ProgramService, Depends(get_program_service)]

router = APIRouter(prefix="/students/{student_id}/program", tags=["program"])


@router.get("", response_model=ProgramResponse)
def get_program(student_id: uuid.UUID, service: ServiceDep, user: CurrentUser) -> ProgramResponse:
    return service.get_for_student(student_id, StudentAccessPolicy.scope_for(user))
