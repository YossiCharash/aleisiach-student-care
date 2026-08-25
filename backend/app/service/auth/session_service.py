import uuid
from datetime import UTC, datetime, timedelta

from backend.app.client.auth.session_repository import SessionRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.models.client.user_session import UserSession
from backend.app.utils.service.token_factory import TokenFactory


class SessionService:
    def __init__(
        self,
        sessions: SessionRepository,
        token_factory: TokenFactory,
        auth_settings: AuthSettings,
    ) -> None:
        self._sessions = sessions
        self._token_factory = token_factory
        self._auth_settings = auth_settings

    def create(self, user_id: uuid.UUID) -> str:
        raw, token_hash = self._token_factory.create()
        ttl = timedelta(minutes=self._auth_settings.session_ttl_minutes)
        self._sessions.add(
            UserSession(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=datetime.now(UTC) + ttl,
            )
        )
        return raw

    def resolve(self, raw_token: str) -> uuid.UUID | None:
        session = self._sessions.find_by_hash(self._token_factory.hash_token(raw_token))
        if session is None or session.revoked_at is not None:
            return None
        if self._as_utc(session.expires_at) <= datetime.now(UTC):
            return None
        return session.user_id

    def revoke(self, raw_token: str) -> None:
        session = self._sessions.find_by_hash(self._token_factory.hash_token(raw_token))
        if session is not None and session.revoked_at is None:
            session.revoked_at = datetime.now(UTC)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
