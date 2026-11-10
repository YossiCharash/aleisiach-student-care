import uuid

from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain


class RiskDomainSeeder:
    def __init__(
        self, domains: RiskDomainRepository, defaults: tuple[tuple[str, str], ...]
    ) -> None:
        self._domains = domains
        self._defaults = defaults

    def seed(self, institution_id: uuid.UUID) -> None:
        orders: dict[RiskCategory, int] = {}
        for category_value, name in self._defaults:
            category = RiskCategory(category_value)
            order = orders.get(category, 0)
            orders[category] = order + 1
            self._domains.add(
                RiskDomain(
                    name=name,
                    category=category,
                    order=order,
                    is_active=True,
                    institution_id=institution_id,
                )
            )
