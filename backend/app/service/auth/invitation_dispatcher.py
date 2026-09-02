import uuid
from datetime import UTC, datetime, timedelta

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.email.email_sender import EmailSender
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.models.client.token_kind import TokenKind
from backend.app.service.auth.token_issuer import TokenIssuer


class InvitationDispatcher:
    def __init__(
        self,
        tokens: AuthTokenRepository,
        token_issuer: TokenIssuer,
        email_sender: EmailSender,
        auth_settings: AuthSettings,
        email_settings: EmailSettings,
    ) -> None:
        self._tokens = tokens
        self._token_issuer = token_issuer
        self._email_sender = email_sender
        self._auth_settings = auth_settings
        self._email_settings = email_settings

    def dispatch(self, user_id: uuid.UUID, email: str) -> None:
        self._tokens.invalidate_pending(user_id, TokenKind.INVITE, datetime.now(UTC))
        ttl = timedelta(hours=self._auth_settings.invite_token_ttl_hours)
        raw_token = self._token_issuer.issue(user_id, TokenKind.INVITE, ttl)
        link = f"{self._email_settings.invite_base_url}?token={raw_token}"
        self._email_sender.send_invitation(email, link)
