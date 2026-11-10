import uuid

from backend.app.client.database.ordered_node_repository import OrderedNodeRepository
from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain


class RiskDomainRepository(OrderedNodeRepository):
    def add(self, domain: RiskDomain) -> RiskDomain:
        return self._add(domain)

    def get(self, domain_id: uuid.UUID) -> RiskDomain | None:
        return self._get(RiskDomain, domain_id)

    def list(self, include_inactive: bool) -> list[RiskDomain]:
        categories = list(RiskCategory)
        domains = self._ordered(RiskDomain, include_inactive)
        return sorted(domains, key=lambda domain: categories.index(domain.category))

    def next_order(self, category: RiskCategory) -> int:
        return self._next_order(RiskDomain, RiskDomain.category == category)
