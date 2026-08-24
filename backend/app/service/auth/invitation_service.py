from datetime import timedelta

from app.client.email.email_sender import EmailSender
from app.client.users.user_repository import UserRepository
from app.configuration.auth.auth_settings import AuthSettings
from app.configuration.email.email_settings import EmailSettings
from app.errors.service.email_already_used_error import EmailAlreadyUsedError
from app.errors.service.invalid_token_error import InvalidTokenError
from app.errors.service.username_already_used_error import UsernameAlreadyUsedError
from app.models.client.token_kind import TokenKind
from app.models.client.user import User
from app.models.client.user_status import UserStatus
from app.schema.routes.user_response import UserResponse
from app.schema.service.invitation_command import InvitationCommand
from app.service.auth.token_consumer import TokenConsumer
from app.service.auth.token_issuer import TokenIssuer
from app.utils.service.password_hasher import PasswordHasher


class InvitationService:
    def __init__(
        self,
        users: UserRepository,
        token_issuer: TokenIssuer,
        token_consumer: TokenConsumer,
        password_hasher: PasswordHasher,
        email_sender: EmailSender,
        auth_settings: AuthSettings,
        email_settings: EmailSettings,
    ) -> None:
        self._users = users
        self._token_issuer = token_issuer
        self._token_consumer = token_consumer
        self._password_hasher = password_hasher
        self._email_sender = email_sender
        self._auth_settings = auth_settings
        self._email_settings = email_settings

    def invite(self, command: InvitationCommand) -> UserResponse:
        if self._users.get_by_email(command.email) is not None:
            raise EmailAlreadyUsedError
        user = self._users.add(
            User(
                full_name=command.full_name,
                email=command.email,
                role=command.role,
                class_id=command.class_id,
                status=UserStatus.INVITED,
            )
        )
        ttl = timedelta(hours=self._auth_settings.invite_token_ttl_hours)
        raw_token = self._token_issuer.issue(user.id, TokenKind.INVITE, ttl)
        link = f"{self._email_settings.invite_base_url}?token={raw_token}"
        self._email_sender.send_invitation(user.email, link)
        return UserResponse.model_validate(user)

    def accept(self, raw_token: str, username: str, password: str) -> UserResponse:
        token = self._token_consumer.consume(raw_token, TokenKind.INVITE)
        user = self._users.get(token.user_id)
        if user is None:
            raise InvalidTokenError
        if self._users.get_by_username(username) is not None:
            raise UsernameAlreadyUsedError
        user.username = username
        user.password_hash = self._password_hasher.hash(password)
        user.status = UserStatus.ACTIVE
        return UserResponse.model_validate(user)
