import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.students.diagnosis_catalog_repository import (
    DiagnosisCatalogRepository,
)
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.diagnosis_catalog_create_request import (
    DiagnosisCatalogCreateRequest,
)
from backend.app.schema.routes.diagnosis_catalog_response import DiagnosisCatalogResponse
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.diagnosis_catalog_service import DiagnosisCatalogService


def get_diagnosis_catalog_service(
    session: Annotated[Session, Depends(get_session)],
) -> DiagnosisCatalogService:
    return DiagnosisCatalogService(
        DiagnosisCatalogRepository(session), AuditLogger(AuditLogRepository(session))
    )


ServiceDep = Annotated[DiagnosisCatalogService, Depends(get_diagnosis_catalog_service)]

router = APIRouter(prefix="/diagnoses", tags=["diagnoses"], dependencies=[Depends(require_tenant)])


@router.get("", response_model=list[DiagnosisCatalogResponse])
def list_diagnoses(
    service: ServiceDep, _: CurrentUser, include_inactive: bool = False
) -> list[DiagnosisCatalogResponse]:
    return service.list_all(include_inactive)


@router.post("", response_model=DiagnosisCatalogResponse, status_code=status.HTTP_201_CREATED)
def create_diagnosis(
    request: DiagnosisCatalogCreateRequest, service: ServiceDep, manager: Manager
) -> DiagnosisCatalogResponse:
    return service.create(request, manager.id)


@router.patch("/{diagnosis_id}", response_model=DiagnosisCatalogResponse)
def update_diagnosis(
    diagnosis_id: uuid.UUID,
    request: OrderedNodeUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> DiagnosisCatalogResponse:
    return service.update(diagnosis_id, request, manager.id)
