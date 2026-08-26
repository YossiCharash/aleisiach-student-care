from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.models.client.audit_log import AuditLog
from backend.app.schema.service.audit_entry import AuditEntry


class AuditLogger:
    def __init__(self, audit_repository: AuditLogRepository) -> None:
        self._audit = audit_repository

    def record(self, entry: AuditEntry) -> None:
        self._audit.add(
            AuditLog(
                actor_id=entry.actor_id,
                action=entry.action,
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                changes=list(entry.changes),
            )
        )
