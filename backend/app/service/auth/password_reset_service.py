from datetime import UTC, datetime, timedelta

from backend.app.client.email.email_sender import EmailSender
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.errors.service.invalid_token_error import InvalidTokenError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.schema.service.password_reset_message import PasswordResetMessage
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.credential_reset_finalizer import CredentialResetFinalizer
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.service.auth.token_issuer import TokenIssuer
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher

_ENTITY_TYPE = "auth"
_PLATFORM_INSTITUTION_NAME = "ניהול המערכת"


class PasswordResetService:
    def __init__(
        self,
        users: UserRepository,
        institutions: InstitutionRepository,
        token_issuer: TokenIssuer,
        token_consumer: TokenConsumer,
        password_hasher: PasswordHasher,
        email_sender: EmailSender,
        auth_settings: AuthSettings,
        email_settings: EmailSettings,
        clock: Clock,
        finalizer: CredentialResetFinalizer,
        audit_logger: AuditLogger,
    ) -> None:
        self._users = users
        self._institutions = institutions
        self._token_issuer = token_issuer
        self._token_consumer = token_consumer
        self._password_hasher = password_hasher
        self._email_sender = email_sender
        self._auth_settings = auth_settings
        self._email_settings = email_settings
        self._clock = clock
        self._finalizer = finalizer
        self._audit = audit_logger

    def request(self, email: str) -> None:
        now = self._clock.now()
        for user in self._users.list_active_by_email(email):
            if not self._recently_requested(user, now):
                self._send(user, now)

    def _send(self, user: User, now: datetime) -> None:
        user.last_reset_request_at = now
        ttl = timedelta(hours=self._auth_settings.reset_token_ttl_hours)
        raw_token = self._token_issuer.issue(user.id, TokenKind.PASSWORD_RESET, ttl)
        self._email_sender.send_password_reset(
            PasswordResetMessage(
                email=user.email,
                link=f"{self._email_settings.reset_base_url}?token={raw_token}",
                institution_name=self._institution_name(user),
                username=user.username or user.full_name,
            )
        )

    def _institution_name(self, user: User) -> str:
        if user.institution_id is None:
            return _PLATFORM_INSTITUTION_NAME
        institution = self._institutions.get(user.institution_id)
        return _PLATFORM_INSTITUTION_NAME if institution is None else institution.name

    def _recently_requested(self, user: User, now: datetime) -> bool:
        last = user.last_reset_request_at
        if last is None:
            return False
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        interval = timedelta(minutes=self._auth_settings.reset_request_interval_minutes)
        return now - last < interval

    def reset(
        self, raw_token: str, new_password: str, context: AuthEventContext | None = None
    ) -> None:
        context = context or AuthEventContext()
        token = self._token_consumer.consume(raw_token, TokenKind.PASSWORD_RESET)
        user = self._users.get(token.user_id)
        if user is None:
            raise InvalidTokenError
        user.password_hash = self._password_hasher.hash(new_password)
        self._finalizer.finalize(user)
        self._audit.record(
            AuditEntry(
                actor_id=user.id,
                action=AuditAction.PASSWORD_RESET,
                entity_type=_ENTITY_TYPE,
                entity_id=user.id,
                ip=context.ip,
                user_agent=context.user_agent,
            )
        )
