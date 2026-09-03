from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest


class OrderedNodeUpdater:
    @staticmethod
    def apply(node: OrderedTaxonomyNode, request: OrderedNodeUpdateRequest) -> list[str]:
        changes: list[str] = []
        for field, value in (
            ("name", request.name),
            ("order", request.order),
            ("is_active", request.is_active),
        ):
            if value is not None:
                setattr(node, field, value)
                changes.append(field)
        return changes
