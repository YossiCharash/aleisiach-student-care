import uuid

from backend.app.client.students.diagnosis_catalog_repository import (
    DiagnosisCatalogRepository,
)
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.diagnosis_catalog import DiagnosisCatalog
from backend.app.schema.routes.diagnosis_catalog_create_request import (
    DiagnosisCatalogCreateRequest,
)
from backend.app.schema.routes.diagnosis_catalog_response import DiagnosisCatalogResponse
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.utils.service.ordered_node_updater import OrderedNodeUpdater

_ENTITY_TYPE = "diagnosis_catalog"


class DiagnosisCatalogService:
    def __init__(self, repository: DiagnosisCatalogRepository, audit_logger: AuditLogger) -> None:
        self._catalog = repository
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)

    def list_all(self, include_inactive: bool) -> list[DiagnosisCatalogResponse]:
        return [
            DiagnosisCatalogResponse.model_validate(entry)
            for entry in self._catalog.list(include_inactive)
        ]

    def create(
        self, request: DiagnosisCatalogCreateRequest, actor_id: uuid.UUID
    ) -> DiagnosisCatalogResponse:
        entry = self._get_or_create(request.name.strip(), actor_id)
        return DiagnosisCatalogResponse.model_validate(entry)

    def update(
        self,
        diagnosis_id: uuid.UUID,
        request: OrderedNodeUpdateRequest,
        actor_id: uuid.UUID,
    ) -> DiagnosisCatalogResponse:
        entry = self._catalog.get(diagnosis_id)
        if entry is None:
            raise NotFoundError("diagnosis")
        changes = OrderedNodeUpdater.apply(entry, request)
        self._catalog.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, entry.id, changes)
        return DiagnosisCatalogResponse.model_validate(entry)

    def ensure_names(self, names: list[str], actor_id: uuid.UUID) -> list[str]:
        resolved: list[str] = []
        for raw in names:
            name = raw.strip()
            if not name or name in resolved:
                continue
            self._get_or_create(name, actor_id)
            resolved.append(name)
        return resolved

    def _get_or_create(self, name: str, actor_id: uuid.UUID) -> DiagnosisCatalog:
        existing = self._catalog.get_by_name(name)
        if existing is not None:
            if not existing.is_active:
                existing.is_active = True
                self._catalog.flush()
                self._audit.record(actor_id, AuditAction.UPDATE, existing.id, ["is_active"])
            return existing
        entry = DiagnosisCatalog(name=name, order=self._catalog.next_order())
        self._catalog.add(entry)
        self._audit.record(actor_id, AuditAction.CREATE, entry.id, ["name"])
        return entry
