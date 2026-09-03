import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.ratelimit.rate_limit_repository import RateLimitRepository
from backend.app.configuration.maintenance.retention_settings import RetentionSettings
from backend.app.configuration.ratelimit.rate_limit_settings import RateLimitSettings
from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user_session import UserSession
from backend.app.service.maintenance.expired_credential_cleanup_service import (
    ExpiredCredentialCleanupService,
)
from backend.tests.support.fake_clock import FakeClock

_NOW = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)


def test_run_deletes_only_records_past_the_retention_window(db_session: Session) -> None:
    sessions = SessionRepository(db_session)
    tokens = AuthTokenRepository(db_session)
    hits = RateLimitRepository(db_session)
    retention = RetentionSettings(expired_credentials_days=30)
    rate_limit = RateLimitSettings(retention_minutes=60)
    stale = _NOW - timedelta(days=31)
    fresh = _NOW - timedelta(days=1)
    hits.add("login:1.2.3.4", _NOW - timedelta(minutes=61))
    hits.add("login:1.2.3.4", _NOW - timedelta(minutes=1))
    sessions.add(UserSession(user_id=uuid.uuid4(), token_hash="s1" * 32, expires_at=stale))
    sessions.add(UserSession(user_id=uuid.uuid4(), token_hash="s2" * 32, expires_at=fresh))
    tokens.add(
        AuthToken(
            user_id=uuid.uuid4(),
            kind=TokenKind.PASSWORD_RESET,
            token_hash="t1" * 32,
            expires_at=stale,
        )
    )

    result = ExpiredCredentialCleanupService(
        sessions, tokens, hits, retention, rate_limit, FakeClock(_NOW)
    ).run()

    assert result.sessions_deleted == 1
    assert result.tokens_deleted == 1
    assert result.rate_limit_hits_deleted == 1
