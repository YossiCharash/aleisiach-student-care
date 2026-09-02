from datetime import timedelta

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.configuration.maintenance.retention_settings import RetentionSettings
from backend.app.schema.service.cleanup_result import CleanupResult
from backend.app.utils.service.clock import Clock


class ExpiredCredentialCleanupService:
    def __init__(
        self,
        sessions: SessionRepository,
        tokens: AuthTokenRepository,
        retention_settings: RetentionSettings,
        clock: Clock,
    ) -> None:
        self._sessions = sessions
        self._tokens = tokens
        self._retention_settings = retention_settings
        self._clock = clock

    def run(self) -> CleanupResult:
        cutoff = self._clock.now() - timedelta(
            days=self._retention_settings.expired_credentials_days
        )
        return CleanupResult(
            sessions_deleted=self._sessions.delete_expired(cutoff),
            tokens_deleted=self._tokens.delete_expired(cutoff),
        )
