import uuid
from datetime import UTC, datetime, timedelta

from app.client.auth.auth_token_repository import AuthTokenRepository
from app.models.client.auth_token import AuthToken
from app.models.client.token_kind import TokenKind
from app.utils.service.token_factory import TokenFactory


class TokenIssuer:
    def __init__(self, tokens: AuthTokenRepository, token_factory: TokenFactory) -> None:
        self._tokens = tokens
        self._token_factory = token_factory

    def issue(self, user_id: uuid.UUID, kind: TokenKind, ttl: timedelta) -> str:
        raw, token_hash = self._token_factory.create()
        self._tokens.add(
            AuthToken(
                user_id=user_id,
                kind=kind,
                token_hash=token_hash,
                expires_at=datetime.now(UTC) + ttl,
            )
        )
        return raw
