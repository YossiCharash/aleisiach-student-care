import uuid
from collections import defaultdict

from backend.app.client.students.extra_section_type_repository import (
    ExtraSectionTypeRepository,
)
from backend.app.errors.service.invalid_section_type_error import InvalidSectionTypeError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.extra_section_type import ExtraSectionType
from backend.app.schema.routes.extra_section_type_create_request import (
    ExtraSectionTypeCreateRequest,
)
from backend.app.schema.routes.extra_section_type_node import ExtraSectionTypeNode
from backend.app.schema.routes.extra_section_type_response import (
    ExtraSectionTypeResponse,
)
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.utils.service.ordered_node_updater import OrderedNodeUpdater

_ENTITY_TYPE = "extra_section_type"


class ExtraSectionTypeService:
    def __init__(
        self, type_repository: ExtraSectionTypeRepository, audit_logger: AuditLogger
    ) -> None:
        self._types = type_repository
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)

    def list_types(self, include_inactive: bool) -> list[ExtraSectionTypeResponse]:
        return [
            ExtraSectionTypeResponse.model_validate(section_type)
            for section_type in self._types.list(include_inactive)
        ]

    def create(
        self, request: ExtraSectionTypeCreateRequest, actor_id: uuid.UUID
    ) -> ExtraSectionTypeResponse:
        if request.parent_id is not None:
            parent = self._types.get(request.parent_id)
            if parent is None:
                raise NotFoundError("section_type")
            if parent.parent_id is not None:
                raise InvalidSectionTypeError("a sub-heading cannot be nested further")
        section_type = ExtraSectionType(
            name=request.name,
            parent_id=request.parent_id,
            order=self._types.next_order(request.parent_id),
        )
        self._types.add(section_type)
        self._audit.record(actor_id, AuditAction.CREATE, section_type.id, ["name"])
        return ExtraSectionTypeResponse.model_validate(section_type)

    def update(
        self,
        section_type_id: uuid.UUID,
        request: OrderedNodeUpdateRequest,
        actor_id: uuid.UUID,
    ) -> ExtraSectionTypeResponse:
        section_type = self._types.get(section_type_id)
        if section_type is None:
            raise NotFoundError("section_type")
        changes = OrderedNodeUpdater.apply(section_type, request)
        self._types.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, section_type.id, changes)
        return ExtraSectionTypeResponse.model_validate(section_type)

    def tree(self) -> list[ExtraSectionTypeNode]:
        active = self._types.list(include_inactive=False)
        children: dict[uuid.UUID, list[ExtraSectionType]] = defaultdict(list)
        headings: list[ExtraSectionType] = []
        for section_type in active:
            if section_type.parent_id is None:
                headings.append(section_type)
            else:
                children[section_type.parent_id].append(section_type)
        return [
            ExtraSectionTypeNode(
                id=heading.id,
                name=heading.name,
                children=[
                    ExtraSectionTypeNode(id=child.id, name=child.name)
                    for child in children[heading.id]
                ],
            )
            for heading in headings
        ]
