import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.workshops.workshop_repository import WorkshopRepository
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.workshop_create_request import WorkshopCreateRequest
from backend.app.schema.routes.workshop_response import WorkshopResponse
from backend.app.schema.routes.workshop_update_request import WorkshopUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.service.workshops.workshop_service import WorkshopService


def get_workshop_service(
    session: Annotated[Session, Depends(get_session)],
) -> WorkshopService:
    return WorkshopService(WorkshopRepository(session), AuditLogger(AuditLogRepository(session)))


ServiceDep = Annotated[WorkshopService, Depends(get_workshop_service)]

router = APIRouter(prefix="/workshops", tags=["workshops"], dependencies=[Depends(require_tenant)])


@router.get("", response_model=list[WorkshopResponse])
def list_workshops(service: ServiceDep, user: CurrentUser) -> list[WorkshopResponse]:
    return service.list_active(StudentAccessPolicy.scope_for(user))


@router.get("/archived", response_model=list[WorkshopResponse])
def list_archived_workshops(service: ServiceDep, _: Manager) -> list[WorkshopResponse]:
    return service.list_archived()


@router.post("", response_model=WorkshopResponse, status_code=status.HTTP_201_CREATED)
def create_workshop(
    request: WorkshopCreateRequest, service: ServiceDep, manager: Manager
) -> WorkshopResponse:
    return service.create(request, manager.id)


@router.patch("/{workshop_id}", response_model=WorkshopResponse)
def update_workshop(
    workshop_id: uuid.UUID,
    request: WorkshopUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> WorkshopResponse:
    return service.update(workshop_id, request, manager.id)


@router.post("/{workshop_id}/archive", response_model=WorkshopResponse)
def archive_workshop(
    workshop_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> WorkshopResponse:
    return service.archive(workshop_id, manager.id)


@router.post("/{workshop_id}/restore", response_model=WorkshopResponse)
def restore_workshop(
    workshop_id: uuid.UUID, service: ServiceDep, manager: Manager
) -> WorkshopResponse:
    return service.restore(workshop_id, manager.id)
