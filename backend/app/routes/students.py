import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.student_create_request import StudentCreateRequest
from backend.app.schema.routes.student_response import StudentResponse
from backend.app.schema.routes.student_update_request import StudentUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.students.student_service import StudentService


def get_student_service(
    session: Annotated[Session, Depends(get_session)],
) -> StudentService:
    return StudentService(
        StudentRepository(session),
        ClassRepository(session),
        StudentDetailsRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[StudentService, Depends(get_student_service)]

router = APIRouter(prefix="/students", tags=["students"], dependencies=[Depends(require_tenant)])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    request: StudentCreateRequest, service: ServiceDep, manager: Manager
) -> StudentResponse:
    return service.create(request, manager.id)


@router.get("", response_model=list[StudentResponse])
def list_students(service: ServiceDep, user: CurrentUser) -> list[StudentResponse]:
    return service.list_active(StudentAccessPolicy.scope_for(user))


@router.get("/archived", response_model=list[StudentResponse])
def list_archived_students(service: ServiceDep, _: Manager) -> list[StudentResponse]:
    return service.list_archived()


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: uuid.UUID, service: ServiceDep, user: CurrentUser) -> StudentResponse:
    return service.get(student_id, StudentAccessPolicy.scope_for(user))


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: uuid.UUID,
    request: StudentUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> StudentResponse:
    return service.update(student_id, request, manager.id)


@router.post("/{student_id}/archive", response_model=StudentResponse)
def archive_student(
    student_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> StudentResponse:
    return service.archive(student_id, manager.id)


@router.post("/{student_id}/restore", response_model=StudentResponse)
def restore_student(
    student_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> StudentResponse:
    return service.restore(student_id, manager.id)
