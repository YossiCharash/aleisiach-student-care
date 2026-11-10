import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.routes.security import CurrentUser, Manager, require_tenant
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.schema.routes.risk_domain_create_request import RiskDomainCreateRequest
from backend.app.schema.routes.risk_domain_response import RiskDomainResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.risk_domain_service import RiskDomainService


def get_risk_domain_service(
    session: Annotated[Session, Depends(get_session)],
) -> RiskDomainService:
    return RiskDomainService(
        RiskDomainRepository(session), AuditLogger(AuditLogRepository(session))
    )


ServiceDep = Annotated[RiskDomainService, Depends(get_risk_domain_service)]

router = APIRouter(
    prefix="/risk-domains",
    tags=["risk-domains"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=list[RiskDomainResponse])
def list_risk_domains(
    service: ServiceDep, _: CurrentUser, include_inactive: bool = False
) -> list[RiskDomainResponse]:
    return service.list_domains(include_inactive)


@router.post("", response_model=RiskDomainResponse, status_code=status.HTTP_201_CREATED)
def create_risk_domain(
    request: RiskDomainCreateRequest, service: ServiceDep, manager: Manager
) -> RiskDomainResponse:
    return service.create(request, manager.id)


@router.patch("/{domain_id}", response_model=RiskDomainResponse)
def update_risk_domain(
    domain_id: uuid.UUID,
    request: OrderedNodeUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> RiskDomainResponse:
    return service.update(domain_id, request, manager.id)
