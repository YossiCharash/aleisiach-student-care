from pydantic import BaseModel

from backend.app.schema.routes.ordered_node_update_request import NodeName


class HealthDomainCreateRequest(BaseModel):
    name: NodeName
