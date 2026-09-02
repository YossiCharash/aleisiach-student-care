import uuid

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.models.client.audit_action import AuditAction
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.credential_reset_finalizer import CredentialResetFinalizer
from backend.app.utils.service.password_hasher import PasswordHasher

_ENTITY_TYPE = "auth"


class PasswordChangeService:
    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasher,
        finalizer: CredentialResetFinalizer,
        audit_logger: AuditLogger,
    ) -> None:
        self._users = users
        self._password_hasher = password_hasher
        self._finalizer = finalizer
        self._audit = audit_logger

    def change(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
        context: AuthEventContext | None = None,
    ) -> None:
        context = context or AuthEventContext()
        user = self._users.get_account(user_id)
        if user is None or user.password_hash is None:
            raise AuthenticationError
        if not self._password_hasher.verify(user.password_hash, current_password):
            raise InvalidCurrentPasswordError
        user.password_hash = self._password_hasher.hash(new_password)
        self._finalizer.finalize(user)
        self._audit.record(
            AuditEntry(
                actor_id=user.id,
                action=AuditAction.PASSWORD_CHANGE,
                entity_type=_ENTITY_TYPE,
                entity_id=user.id,
                ip=context.ip,
                user_agent=context.user_agent,
            )
        )
