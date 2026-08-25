import pytest
from sqlalchemy.orm import Session

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.errors.service.email_already_used_error import EmailAlreadyUsedError
from backend.app.errors.service.invalid_token_error import InvalidTokenError
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.service.invitation_command import InvitationCommand
from backend.app.service.auth.invitation_service import InvitationService
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.service.auth.token_issuer import TokenIssuer
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.service.capturing_email_sender import CapturingEmailSender


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
