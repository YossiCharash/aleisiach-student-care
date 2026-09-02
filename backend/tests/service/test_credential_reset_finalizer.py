from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_session import UserSession
from backend.app.models.client.user_status import UserStatus
from backend.app.service.auth.credential_reset_finalizer import CredentialResetFinalizer
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.tests.support.fake_clock import FakeClock

_NOW = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)


def _user(session: Session) -> User:
    user = User(
        full_name="User",
        email="u@example.com",
        username="u",
        password_hash=PasswordHasher().hash("x"),
        role=UserRole.MANAGER,
        status=UserStatus.ACTIVE,
        failed_login_count=3,
        locked_until=_NOW + timedelta(minutes=10),
    )
    session.add(user)
    session.flush()
    return user


def test_finalize_revokes_sessions_invalidates_tokens_and_clears_lockout(
    db_session: Session,
) -> None:
    user = _user(db_session)
    sessions = SessionRepository(db_session)
    tokens = AuthTokenRepository(db_session)
    live = sessions.add(
        UserSession(user_id=user.id, token_hash="a" * 64, expires_at=_NOW + timedelta(hours=1))
    )
    pending = tokens.add(
        AuthToken(
            user_id=user.id,
            kind=TokenKind.PASSWORD_RESET,
            token_hash="b" * 64,
            expires_at=_NOW + timedelta(hours=1),
        )
    )

    CredentialResetFinalizer(sessions, tokens, FakeClock(_NOW)).finalize(user)

    assert user.failed_login_count == 0
    assert user.locked_until is None

    live_id = live.id
    pending_id = pending.id
    db_session.expire_all()
    refreshed_session = db_session.get(UserSession, live_id)
    refreshed_token = db_session.get(AuthToken, pending_id)
    assert refreshed_session is not None and refreshed_session.revoked_at is not None
    assert refreshed_token is not None and refreshed_token.used_at is not None
