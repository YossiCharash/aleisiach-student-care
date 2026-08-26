from datetime import UTC, timedelta

from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.errors.service.account_locked_error import AccountLockedError
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher


class AuthenticationService:
    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasher,
        auth_settings: AuthSettings,
        clock: Clock,
    ) -> None:
        self._users = users
        self._password_hasher = password_hasher
        self._auth_settings = auth_settings
        self._clock = clock

    def authenticate(self, username: str, password: str) -> UserResponse:
        user = self._users.get_by_username(username)
        if user is None or user.status != UserStatus.ACTIVE or user.password_hash is None:
            raise AuthenticationError
        if self._is_locked(user):
            raise AccountLockedError
        if not self._password_hasher.verify(user.password_hash, password):
            self._register_failure(user)
            raise AuthenticationError
        user.failed_login_count = 0
        user.locked_until = None
        return UserResponse.model_validate(user)

    def _is_locked(self, user: User) -> bool:
        if user.locked_until is None:
            return False
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        return self._clock.now() < locked_until

    def _register_failure(self, user: User) -> None:
        user.failed_login_count += 1
        if user.failed_login_count >= self._auth_settings.max_failed_logins:
            user.locked_until = self._clock.now() + timedelta(
                minutes=self._auth_settings.lockout_minutes
            )
            user.failed_login_count = 0
        self._users.commit()
