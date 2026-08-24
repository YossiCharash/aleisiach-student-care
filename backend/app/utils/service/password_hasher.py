from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import Argon2Error


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
