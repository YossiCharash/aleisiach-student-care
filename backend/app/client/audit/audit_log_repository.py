import uuid

from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user import User


class AuditLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: AuditLog) -> AuditLog:
        if entry.institution_id is None:
            entry.institution_id = self._owner_of(entry.actor_id)
        self._session.add(entry)
        self._session.flush()
        return entry

    def _owner_of(self, actor_id: uuid.UUID) -> uuid.UUID | None:
        bound = TenantBinding.current(self._session)
        if bound is not None:
            return bound
        with TenantBinding.platform(self._session):
            actor = self._session.get(User, actor_id)
        return None if actor is None else actor.institution_id
