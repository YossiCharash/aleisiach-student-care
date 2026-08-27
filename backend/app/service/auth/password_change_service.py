import uuid

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.utils.service.password_hasher import PasswordHasher


class PasswordChangeService:
    def __init__(self, users: UserRepository, password_hasher: PasswordHasher) -> None:
        self._users = users
        self._password_hasher = password_hasher

    def change(self, user_id: uuid.UUID, current_password: str, new_password: str) -> None:
        user = self._users.get(user_id)
        if user is None or user.password_hash is None:
            raise AuthenticationError
        if not self._password_hasher.verify(user.password_hash, current_password):
            raise InvalidCurrentPasswordError
        user.password_hash = self._password_hasher.hash(new_password)
