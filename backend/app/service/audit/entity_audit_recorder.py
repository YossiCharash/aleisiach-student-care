import uuid

from backend.app.models.client.audit_action import AuditAction
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger


class EntityAuditRecorder:
    def __init__(self, audit_logger: AuditLogger, entity_type: str) -> None:
        self._audit = audit_logger
        self._entity_type = entity_type

    def record(
        self,
        actor_id: uuid.UUID,
        action: AuditAction,
        entity_id: uuid.UUID,
        changes: list[str],
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=self._entity_type,
                entity_id=entity_id,
                changes=changes,
            )
        )
