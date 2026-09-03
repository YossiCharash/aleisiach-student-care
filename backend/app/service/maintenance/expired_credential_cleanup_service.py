from datetime import timedelta

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.ratelimit.rate_limit_repository import RateLimitRepository
from backend.app.configuration.maintenance.retention_settings import RetentionSettings
from backend.app.configuration.ratelimit.rate_limit_settings import RateLimitSettings
from backend.app.schema.service.cleanup_result import CleanupResult
from backend.app.utils.service.clock import Clock


class ExpiredCredentialCleanupService:
    def __init__(
        self,
        sessions: SessionRepository,
        tokens: AuthTokenRepository,
        rate_limit_hits: RateLimitRepository,
        retention_settings: RetentionSettings,
        rate_limit_settings: RateLimitSettings,
        clock: Clock,
    ) -> None:
        self._sessions = sessions
        self._tokens = tokens
        self._rate_limit_hits = rate_limit_hits
        self._retention_settings = retention_settings
        self._rate_limit_settings = rate_limit_settings
        self._clock = clock

    def run(self) -> CleanupResult:
        now = self._clock.now()
        cutoff = now - timedelta(days=self._retention_settings.expired_credentials_days)
        hits_cutoff = now - timedelta(minutes=self._rate_limit_settings.retention_minutes)
        return CleanupResult(
            sessions_deleted=self._sessions.delete_expired(cutoff),
            tokens_deleted=self._tokens.delete_expired(cutoff),
            rate_limit_hits_deleted=self._rate_limit_hits.delete_before(hits_cutoff),
        )
