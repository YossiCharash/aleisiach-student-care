from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: AuditLog) -> AuditLog:
        if entry.institution_id is None:
            entry.institution_id = TenantBinding.current(self._session)
        self._session.add(entry)
        self._session.flush()
        return entry
