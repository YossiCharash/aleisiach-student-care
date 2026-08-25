from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.utils.service.password_hasher import PasswordHasher


class AuthenticationService:
    def __init__(self, users: UserRepository, password_hasher: PasswordHasher) -> None:
        self._users = users
        self._password_hasher = password_hasher

    def authenticate(self, username: str, password: str) -> UserResponse:
        user = self._users.get_by_username(username)
        if not self._is_valid(user, password):
            raise AuthenticationError
        return UserResponse.model_validate(user)

    def _is_valid(self, user: User | None, password: str) -> bool:
        if user is None or user.status != UserStatus.ACTIVE or user.password_hash is None:
            return False
        return self._password_hasher.verify(user.password_hash, password)
