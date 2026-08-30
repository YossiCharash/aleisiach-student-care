import secrets

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import Argon2Error


class PasswordHasher:
    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher()
        self._dummy_hash = self._hasher.hash(secrets.token_urlsafe(16))

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except Argon2Error:
            return False

    def verify_dummy(self, password: str) -> None:
        self.verify(self._dummy_hash, password)
