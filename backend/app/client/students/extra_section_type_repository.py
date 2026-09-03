import uuid

from backend.app.client.database.ordered_node_repository import OrderedNodeRepository
from backend.app.models.client.extra_section_type import ExtraSectionType


class ExtraSectionTypeRepository(OrderedNodeRepository):
    def add(self, section_type: ExtraSectionType) -> ExtraSectionType:
        return self._add(section_type)

    def get(self, section_type_id: uuid.UUID) -> ExtraSectionType | None:
        return self._get(ExtraSectionType, section_type_id)

    def list(self, include_inactive: bool) -> list[ExtraSectionType]:
        return self._ordered(ExtraSectionType, include_inactive)

    def next_order(self, parent_id: uuid.UUID | None) -> int:
        sibling = (
            ExtraSectionType.parent_id.is_(None)
            if parent_id is None
            else ExtraSectionType.parent_id == parent_id
        )
        return self._next_order(ExtraSectionType, sibling)
