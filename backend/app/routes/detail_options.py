import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.detail_option_repository import DetailOptionRepository
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.detail_option_create_request import (
    DetailOptionCreateRequest,
)
from backend.app.schema.routes.detail_option_response import DetailOptionResponse
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.detail_option_service import DetailOptionService


def get_detail_option_service(
    session: Annotated[Session, Depends(get_session)],
) -> DetailOptionService:
    return DetailOptionService(
        DetailOptionRepository(session), AuditLogger(AuditLogRepository(session))
    )


ServiceDep = Annotated[DetailOptionService, Depends(get_detail_option_service)]

router = APIRouter(
    prefix="/detail-options", tags=["detail-options"], dependencies=[Depends(require_tenant)]
)


@router.get("", response_model=list[DetailOptionResponse])
def list_options(
    service: ServiceDep, _: CurrentUser, include_inactive: bool = False
) -> list[DetailOptionResponse]:
    return service.list_all(include_inactive)


@router.post("", response_model=DetailOptionResponse, status_code=status.HTTP_201_CREATED)
def create_option(
    request: DetailOptionCreateRequest, service: ServiceDep, manager: Manager
) -> DetailOptionResponse:
    return service.create(request, manager.id)


@router.patch("/{option_id}", response_model=DetailOptionResponse)
def update_option(
    option_id: uuid.UUID,
    request: OrderedNodeUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> DetailOptionResponse:
    return service.update(option_id, request, manager.id)
