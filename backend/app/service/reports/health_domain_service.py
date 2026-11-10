import uuid

from backend.app.client.reports.health_domain_repository import HealthDomainRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.health_domain import HealthDomain
from backend.app.schema.routes.health_domain_create_request import HealthDomainCreateRequest
from backend.app.schema.routes.health_domain_response import HealthDomainResponse
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.utils.service.ordered_node_updater import OrderedNodeUpdater

_ENTITY_TYPE = "health_domain"


class HealthDomainService:
    def __init__(
        self, domain_repository: HealthDomainRepository, audit_logger: AuditLogger
    ) -> None:
        self._domains = domain_repository
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)

    def list_domains(self, include_inactive: bool) -> list[HealthDomainResponse]:
        return [
            HealthDomainResponse.model_validate(domain)
            for domain in self._domains.list(include_inactive)
        ]

    def create(
        self, request: HealthDomainCreateRequest, actor_id: uuid.UUID
    ) -> HealthDomainResponse:
        domain = HealthDomain(name=request.name, order=self._domains.next_order())
        self._domains.add(domain)
        self._audit.record(actor_id, AuditAction.CREATE, domain.id, ["name"])
        return HealthDomainResponse.model_validate(domain)

    def update(
        self, domain_id: uuid.UUID, request: OrderedNodeUpdateRequest, actor_id: uuid.UUID
    ) -> HealthDomainResponse:
        domain = self._domains.get(domain_id)
        if domain is None:
            raise NotFoundError("health_domain")
        changes = OrderedNodeUpdater.apply(domain, request)
        self._domains.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, domain.id, changes)
        return HealthDomainResponse.model_validate(domain)
