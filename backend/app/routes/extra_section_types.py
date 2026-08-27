import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.extra_section_type_repository import (
    ExtraSectionTypeRepository,
)
from backend.app.routes.security import CurrentUser, Manager
from backend.app.schema.routes.extra_section_type_create_request import (
    ExtraSectionTypeCreateRequest,
)
from backend.app.schema.routes.extra_section_type_node import ExtraSectionTypeNode
from backend.app.schema.routes.extra_section_type_response import (
    ExtraSectionTypeResponse,
)
from backend.app.schema.routes.extra_section_type_update_request import (
    ExtraSectionTypeUpdateRequest,
)
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.extra_section_type_service import (
    ExtraSectionTypeService,
)


def get_extra_section_type_service(
    session: Annotated[Session, Depends(get_session)],
) -> ExtraSectionTypeService:
    return ExtraSectionTypeService(
        ExtraSectionTypeRepository(session), AuditLogger(AuditLogRepository(session))
    )


ServiceDep = Annotated[ExtraSectionTypeService, Depends(get_extra_section_type_service)]

router = APIRouter(prefix="/extra-section-types", tags=["extra-section-types"])


@router.get("/tree", response_model=list[ExtraSectionTypeNode])
def get_tree(service: ServiceDep, _: CurrentUser) -> list[ExtraSectionTypeNode]:
    return service.tree()


@router.get("", response_model=list[ExtraSectionTypeResponse])
def list_types(
    service: ServiceDep, _: CurrentUser, include_inactive: bool = False
) -> list[ExtraSectionTypeResponse]:
    return service.list_types(include_inactive)


@router.post("", response_model=ExtraSectionTypeResponse, status_code=status.HTTP_201_CREATED)
def create_type(
    request: ExtraSectionTypeCreateRequest, service: ServiceDep, manager: Manager
) -> ExtraSectionTypeResponse:
    return service.create(request, manager.id)


@router.patch("/{section_type_id}", response_model=ExtraSectionTypeResponse)
def update_type(
    section_type_id: uuid.UUID,
    request: ExtraSectionTypeUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> ExtraSectionTypeResponse:
    return service.update(section_type_id, request, manager.id)
