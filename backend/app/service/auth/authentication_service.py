from datetime import UTC, timedelta

from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher

_ENTITY_TYPE = "auth"


class AuthenticationService:
    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasher,
        auth_settings: AuthSettings,
        clock: Clock,
        audit_logger: AuditLogger,
    ) -> None:
        self._users = users
        self._password_hasher = password_hasher
        self._auth_settings = auth_settings
        self._clock = clock
        self._audit = audit_logger

    def authenticate(
        self, username: str, password: str, context: AuthEventContext | None = None
    ) -> UserResponse:
        context = context or AuthEventContext()
        user = self._users.get_by_username(username)
        if user is None or user.status != UserStatus.ACTIVE or user.password_hash is None:
            self._password_hasher.verify_dummy(password)
            self._users.commit()
            raise AuthenticationError
        if self._is_locked(user):
            self._password_hasher.verify_dummy(password)
            self._record(user, AuditAction.LOGIN_FAILED, context)
            self._users.commit()
            raise AuthenticationError
        if not self._password_hasher.verify(user.password_hash, password):
            self._register_failure(user, context)
            raise AuthenticationError
        user.failed_login_count = 0
        user.locked_until = None
        self._record(user, AuditAction.LOGIN, context)
        return UserResponse.model_validate(user)

    def _is_locked(self, user: User) -> bool:
        if user.locked_until is None:
            return False
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        return self._clock.now() < locked_until

    def _register_failure(self, user: User, context: AuthEventContext) -> None:
        user.failed_login_count += 1
        self._record(user, AuditAction.LOGIN_FAILED, context)
        if user.failed_login_count >= self._auth_settings.max_failed_logins:
            user.locked_until = self._clock.now() + timedelta(
                minutes=self._auth_settings.lockout_minutes
            )
            user.failed_login_count = 0
            self._record(user, AuditAction.LOCKOUT, context)
        self._users.commit()

    def _record(self, user: User, action: AuditAction, context: AuthEventContext) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=user.id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=user.id,
                ip=context.ip,
                user_agent=context.user_agent,
            )
        )
