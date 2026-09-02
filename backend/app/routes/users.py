import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.database.provider import get_session
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.routes.auth import build_invitation_dispatcher
from backend.app.routes.security import Manager
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.routes.user_update_request import UserUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.users.user_management_service import UserManagementService


def get_user_management_service(
    session: Annotated[Session, Depends(get_session)],
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> UserManagementService:
    return UserManagementService(
        UserRepository(session),
        ClassRepository(session),
        build_invitation_dispatcher(session, bootstrap),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[UserManagementService, Depends(get_user_management_service)]

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(service: ServiceDep, _: Manager) -> list[UserResponse]:
    return service.list_users()


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    request: UserUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> UserResponse:
    return service.update(user_id, request, manager.id)


@router.post("/{user_id}/disable", response_model=UserResponse)
def disable_user(user_id: uuid.UUID, service: ServiceDep, manager: Manager) -> UserResponse:
    return service.disable(user_id, manager.id)


@router.post("/{user_id}/enable", response_model=UserResponse)
def enable_user(user_id: uuid.UUID, service: ServiceDep, manager: Manager) -> UserResponse:
    return service.enable(user_id, manager.id)
