import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.health_domain_repository import HealthDomainRepository
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.health_domain_create_request import HealthDomainCreateRequest
from backend.app.schema.routes.health_domain_response import HealthDomainResponse
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.health_domain_service import HealthDomainService


def get_health_domain_service(
    session: Annotated[Session, Depends(get_session)],
) -> HealthDomainService:
    return HealthDomainService(
        HealthDomainRepository(session), AuditLogger(AuditLogRepository(session))
    )


ServiceDep = Annotated[HealthDomainService, Depends(get_health_domain_service)]

router = APIRouter(
    prefix="/health-domains",
    tags=["health-domains"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=list[HealthDomainResponse])
def list_health_domains(
    service: ServiceDep, _: CurrentUser, include_inactive: bool = False
) -> list[HealthDomainResponse]:
    return service.list_domains(include_inactive)


@router.post("", response_model=HealthDomainResponse, status_code=status.HTTP_201_CREATED)
def create_health_domain(
    request: HealthDomainCreateRequest, service: ServiceDep, manager: Manager
) -> HealthDomainResponse:
    return service.create(request, manager.id)


@router.patch("/{domain_id}", response_model=HealthDomainResponse)
def update_health_domain(
    domain_id: uuid.UUID,
    request: OrderedNodeUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> HealthDomainResponse:
    return service.update(domain_id, request, manager.id)
