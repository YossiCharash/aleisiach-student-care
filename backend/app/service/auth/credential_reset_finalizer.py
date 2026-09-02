from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.utils.service.clock import Clock


class CredentialResetFinalizer:
    def __init__(
        self,
        sessions: SessionRepository,
        tokens: AuthTokenRepository,
        clock: Clock,
    ) -> None:
        self._sessions = sessions
        self._tokens = tokens
        self._clock = clock

    def finalize(self, user: User) -> None:
        now = self._clock.now()
        self._sessions.revoke_all_for_user(user.id, now)
        self._tokens.invalidate_pending(user.id, TokenKind.PASSWORD_RESET, now)
        user.failed_login_count = 0
        user.locked_until = None
