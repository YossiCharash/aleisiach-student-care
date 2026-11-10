from pydantic import BaseModel

from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain


class RiskDomainResponse(BaseModel):
    domain: RiskDomain
    category: RiskCategory
    category_label: str
    label: str
