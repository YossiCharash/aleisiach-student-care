import uuid

from backend.app.client.database.ordered_node_repository import OrderedNodeRepository
from backend.app.models.client.health_domain import HealthDomain


class HealthDomainRepository(OrderedNodeRepository):
    def add(self, domain: HealthDomain) -> HealthDomain:
        return self._add(domain)

    def get(self, domain_id: uuid.UUID) -> HealthDomain | None:
        return self._get(HealthDomain, domain_id)

    def list(self, include_inactive: bool) -> list[HealthDomain]:
        return self._ordered(HealthDomain, include_inactive)

    def next_order(self) -> int:
        return self._next_order(HealthDomain)
