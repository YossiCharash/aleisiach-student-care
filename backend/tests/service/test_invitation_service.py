import pytest
from app.client.auth.auth_token_repository import AuthTokenRepository
from app.client.users.user_repository import UserRepository
from app.configuration.auth.auth_settings import AuthSettings
from app.configuration.email.email_settings import EmailSettings
from app.errors.service.email_already_used_error import EmailAlreadyUsedError
from app.errors.service.invalid_token_error import InvalidTokenError
from app.models.client.user_role import UserRole
from app.models.client.user_status import UserStatus
from app.schema.service.invitation_command import InvitationCommand
from app.service.auth.invitation_service import InvitationService
from app.service.auth.token_consumer import TokenConsumer
from app.service.auth.token_issuer import TokenIssuer
from app.utils.service.password_hasher import PasswordHasher
from app.utils.service.token_factory import TokenFactory
from sqlalchemy.orm import Session

from tests.service.capturing_email_sender import CapturingEmailSender


def _service(session: Session, sender: CapturingEmailSender) -> InvitationService:
    tokens = AuthTokenRepository(session)
    factory = TokenFactory()
    return InvitationService(
        UserRepository(session),
        TokenIssuer(tokens, factory),
        TokenConsumer(tokens, factory),
        PasswordHasher(),
        sender,
        AuthSettings(),
        EmailSettings(),
    )


def test_invite_then_accept_activates_user(db_session: Session) -> None:
    sender = CapturingEmailSender()
    service = _service(db_session, sender)

    invited = service.invite(
        InvitationCommand(full_name="Manager", email="m@example.com", role=UserRole.MANAGER)
    )
    assert invited.status == UserStatus.INVITED
    assert sender.invitation_link is not None

    token = CapturingEmailSender.token_from(sender.invitation_link)
    activated = service.accept(token, "manager1", "password123")

    assert activated.status == UserStatus.ACTIVE
    assert activated.username == "manager1"


def test_invite_duplicate_email_raises(db_session: Session) -> None:
    service = _service(db_session, CapturingEmailSender())
    command = InvitationCommand(full_name="M", email="dup@example.com", role=UserRole.MANAGER)
    service.invite(command)

    with pytest.raises(EmailAlreadyUsedError):
        service.invite(command)


def test_accept_with_unknown_token_raises(db_session: Session) -> None:
    service = _service(db_session, CapturingEmailSender())

    with pytest.raises(InvalidTokenError):
        service.accept("not-a-real-token", "someone", "password123")
