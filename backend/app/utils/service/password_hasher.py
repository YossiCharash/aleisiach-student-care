import secrets

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import Argon2Error

_DUMMY_HASH = Argon2PasswordHasher().hash(secrets.token_urlsafe(16))


class PasswordHasher:
    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except Argon2Error:
            return False

    def verify_dummy(self, password: str) -> None:
        self.verify(_DUMMY_HASH, password)
