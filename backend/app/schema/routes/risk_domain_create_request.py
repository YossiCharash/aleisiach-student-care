from pydantic import BaseModel

from backend.app.models.client.risk_category import RiskCategory
from backend.app.schema.routes.ordered_node_update_request import NodeName


class RiskDomainCreateRequest(BaseModel):
    name: NodeName
    category: RiskCategory
