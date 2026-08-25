import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.student_repository import StudentRepository
from backend.app.schema.routes.student_create_request import StudentCreateRequest
from backend.app.schema.routes.student_response import StudentResponse
from backend.app.service.students.student_service import StudentService


def get_student_service(
    session: Annotated[Session, Depends(get_session)],
) -> StudentService:
    return StudentService(StudentRepository(session), ClassRepository(session))


ServiceDep = Annotated[StudentService, Depends(get_student_service)]

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(request: StudentCreateRequest, service: ServiceDep) -> StudentResponse:
    return service.create(request)


@router.get("", response_model=list[StudentResponse])
def list_students(service: ServiceDep) -> list[StudentResponse]:
    return service.list_active()


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: uuid.UUID, service: ServiceDep) -> StudentResponse:
    return service.get(student_id)


@router.post("/{student_id}/archive", response_model=StudentResponse)
def archive_student(student_id: uuid.UUID, service: ServiceDep) -> StudentResponse:
    return service.archive(student_id)
