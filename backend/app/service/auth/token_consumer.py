from datetime import UTC, datetime

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.errors.service.invalid_token_error import InvalidTokenError
from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.token_kind import TokenKind
from backend.app.utils.service.token_factory import TokenFactory


class TokenConsumer:
    def __init__(self, tokens: AuthTokenRepository, token_factory: TokenFactory) -> None:
        self._tokens = tokens
        self._token_factory = token_factory

    def consume(self, raw_token: str, kind: TokenKind) -> AuthToken:
        token = self._tokens.find_by_hash(self._token_factory.hash_token(raw_token))
        now = datetime.now(UTC)
        if (
            token is None
            or token.kind != kind
            or token.used_at is not None
            or self._as_utc(token.expires_at) <= now
        ):
            raise InvalidTokenError
        token.used_at = now
        return token

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
