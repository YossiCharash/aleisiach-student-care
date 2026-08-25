from sqlalchemy.orm import Session

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.service.auth.password_reset_service import PasswordResetService
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.service.auth.token_issuer import TokenIssuer
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.service.capturing_email_sender import CapturingEmailSender


def _service(
    session: Session, hasher: PasswordHasher, sender: CapturingEmailSender
) -> PasswordResetService:
    tokens = AuthTokenRepository(session)
    factory = TokenFactory()
    return PasswordResetService(
        UserRepository(session),
        TokenIssuer(tokens, factory),
        TokenConsumer(tokens, factory),
        hasher,
        sender,
        AuthSettings(),
        EmailSettings(),
    )


def _seed_active_user(session: Session, hasher: PasswordHasher) -> None:
    session.add(
        User(
            full_name="Manager",
            email="m@example.com",
            username="manager1",
            password_hash=hasher.hash("old-password"),
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
    )
    session.flush()


def test_request_then_reset_changes_password(db_session: Session) -> None:
    hasher = PasswordHasher()
    sender = CapturingEmailSender()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, sender)

    service.request("m@example.com")
    assert sender.reset_link is not None

    token = CapturingEmailSender.token_from(sender.reset_link)
    service.reset(token, "new-password")

    user = UserRepository(db_session).get_by_username("manager1")
    assert user is not None
    assert user.password_hash is not None
    assert hasher.verify(user.password_hash, "new-password") is True


def test_request_unknown_email_sends_nothing(db_session: Session) -> None:
    sender = CapturingEmailSender()
    service = _service(db_session, PasswordHasher(), sender)

    service.request("nobody@example.com")

    assert sender.reset_link is None
