import uuid

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.errors.service.email_already_used_error import EmailAlreadyUsedError
from backend.app.errors.service.invalid_token_error import InvalidTokenError
from backend.app.errors.service.username_already_used_error import UsernameAlreadyUsedError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.schema.service.invitation_command import InvitationCommand
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.utils.service.password_hasher import PasswordHasher

_ENTITY_TYPE = "permission"


class InvitationService:
    def __init__(
        self,
        users: UserRepository,
        invitation_dispatcher: InvitationDispatcher,
        token_consumer: TokenConsumer,
        password_hasher: PasswordHasher,
        audit_logger: AuditLogger,
    ) -> None:
        self._users = users
        self._dispatcher = invitation_dispatcher
        self._token_consumer = token_consumer
        self._password_hasher = password_hasher
        self._audit = audit_logger

    def invite(self, command: InvitationCommand, actor_id: uuid.UUID) -> UserResponse:
        if command.role == UserRole.SUPER_ADMIN:
            raise AuthorizationError
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
        self._dispatcher.dispatch(user.id, user.email)
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=user.id,
                changes=["role", "class_id"] if command.class_id else ["role"],
            )
        )
        return UserResponse.model_validate(user)

    def accept(
        self,
        raw_token: str,
        username: str,
        password: str,
        context: AuthEventContext | None = None,
    ) -> UserResponse:
        context = context or AuthEventContext()
        token = self._token_consumer.consume(raw_token, TokenKind.INVITE)
        user = self._users.get(token.user_id)
        if user is None or user.status is not UserStatus.INVITED:
            raise InvalidTokenError
        if self._users.get_by_username(username) is not None:
            raise UsernameAlreadyUsedError
        user.username = username
        user.password_hash = self._password_hasher.hash(password)
        user.status = UserStatus.ACTIVE
        self._audit.record(
            AuditEntry(
                actor_id=user.id,
                action=AuditAction.INVITATION_ACCEPTED,
                entity_type="auth",
                entity_id=user.id,
                ip=context.ip,
                user_agent=context.user_agent,
            )
        )
        return UserResponse.model_validate(user)
