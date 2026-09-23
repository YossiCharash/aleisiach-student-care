import uuid

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.utils.service.password_hasher import PasswordHasher


class PasswordVerifier:
    def __init__(self, users: UserRepository, password_hasher: PasswordHasher) -> None:
        self._users = users
        self._password_hasher = password_hasher

    def verify(self, actor_id: uuid.UUID, password: str) -> None:
        actor = self._users.get_account(actor_id)
        if actor is None or actor.password_hash is None:
            raise AuthenticationError
        if not self._password_hasher.verify(actor.password_hash, password):
            raise InvalidCurrentPasswordError
