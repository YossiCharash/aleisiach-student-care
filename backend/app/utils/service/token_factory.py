import hashlib
import secrets


class TokenFactory:
    def create(self) -> tuple[str, str]:
        raw = secrets.token_urlsafe(32)
        return raw, self.hash_token(raw)

    def hash_token(self, raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
