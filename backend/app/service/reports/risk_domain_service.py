import uuid

from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.risk_domain import RiskDomain
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.schema.routes.risk_domain_create_request import RiskDomainCreateRequest
from backend.app.schema.routes.risk_domain_response import RiskDomainResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.utils.service.ordered_node_updater import OrderedNodeUpdater

_ENTITY_TYPE = "risk_domain"


class RiskDomainService:
    def __init__(self, domain_repository: RiskDomainRepository, audit_logger: AuditLogger) -> None:
        self._domains = domain_repository
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)

    def list_domains(self, include_inactive: bool) -> list[RiskDomainResponse]:
        return [
            RiskDomainResponse.model_validate(domain)
            for domain in self._domains.list(include_inactive)
        ]

    def create(self, request: RiskDomainCreateRequest, actor_id: uuid.UUID) -> RiskDomainResponse:
        domain = RiskDomain(
            name=request.name,
            category=request.category,
            order=self._domains.next_order(request.category),
        )
        self._domains.add(domain)
        self._audit.record(actor_id, AuditAction.CREATE, domain.id, ["name", "category"])
        return RiskDomainResponse.model_validate(domain)

    def update(
        self, domain_id: uuid.UUID, request: OrderedNodeUpdateRequest, actor_id: uuid.UUID
    ) -> RiskDomainResponse:
        domain = self._domains.get(domain_id)
        if domain is None:
            raise NotFoundError("risk_domain")
        changes = OrderedNodeUpdater.apply(domain, request)
        self._domains.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, domain.id, changes)
        return RiskDomainResponse.model_validate(domain)
