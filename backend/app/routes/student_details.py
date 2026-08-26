import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.client.database.provider import get_session
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.security import ContentWriter, CurrentUser
from backend.app.schema.routes.student_details_response import StudentDetailsResponse
from backend.app.schema.routes.student_details_upsert_request import (
    StudentDetailsUpsertRequest,
)
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.students.student_details_service import StudentDetailsService


def get_student_details_service(
    session: Annotated[Session, Depends(get_session)],
) -> StudentDetailsService:
    return StudentDetailsService(
        StudentDetailsRepository(session), StudentAccessGuard(StudentRepository(session))
    )


ServiceDep = Annotated[StudentDetailsService, Depends(get_student_details_service)]

router = APIRouter(prefix="/students/{student_id}/details", tags=["student-details"])


@router.get("", response_model=StudentDetailsResponse)
def get_details(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> StudentDetailsResponse:
    return service.get(
        student_id,
        StudentAccessPolicy.scope_for(user),
        StudentAccessPolicy.can_see_sensitive(user),
    )


@router.put("", response_model=StudentDetailsResponse)
def upsert_details(
    student_id: uuid.UUID,
    request: StudentDetailsUpsertRequest,
    service: ServiceDep,
    writer: ContentWriter,
) -> StudentDetailsResponse:
    return service.upsert(student_id, request, StudentAccessPolicy.scope_for(writer))
