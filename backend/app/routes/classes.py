import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.database.provider import get_session
from backend.app.routes.security import CurrentUser, Manager
from backend.app.schema.routes.class_create_request import ClassCreateRequest
from backend.app.schema.routes.class_response import ClassResponse
from backend.app.schema.routes.class_update_request import ClassUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.classes.class_service import ClassService


def get_class_service(
    session: Annotated[Session, Depends(get_session)],
) -> ClassService:
    return ClassService(ClassRepository(session), AuditLogger(AuditLogRepository(session)))


ServiceDep = Annotated[ClassService, Depends(get_class_service)]

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("", response_model=list[ClassResponse])
def list_classes(service: ServiceDep, _: CurrentUser) -> list[ClassResponse]:
    return service.list_active()


@router.get("/archived", response_model=list[ClassResponse])
def list_archived_classes(service: ServiceDep, _: Manager) -> list[ClassResponse]:
    return service.list_archived()


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    request: ClassCreateRequest, service: ServiceDep, manager: Manager
) -> ClassResponse:
    return service.create(request, manager.id)


@router.patch("/{class_id}", response_model=ClassResponse)
def rename_class(
    class_id: uuid.UUID,
    request: ClassUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> ClassResponse:
    return service.rename(class_id, request, manager.id)


@router.post("/{class_id}/archive", response_model=ClassResponse)
def archive_class(class_id: uuid.UUID, service: ServiceDep, manager: Manager) -> ClassResponse:
    return service.archive(class_id, manager.id)


@router.post("/{class_id}/restore", response_model=ClassResponse)
def restore_class(class_id: uuid.UUID, service: ServiceDep, manager: Manager) -> ClassResponse:
    return service.restore(class_id, manager.id)
