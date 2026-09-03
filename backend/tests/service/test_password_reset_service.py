from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.models.client.institution import Institution
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.credential_reset_finalizer import CredentialResetFinalizer
from backend.app.service.auth.password_reset_service import PasswordResetService
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.service.auth.token_issuer import TokenIssuer
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.conftest import DEFAULT_INSTITUTION_ID
from backend.tests.service.capturing_email_sender import CapturingEmailSender

_BASE = datetime(2026, 8, 27, 9, 0, tzinfo=UTC)


class _FakeClock(Clock):
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def now(self) -> datetime:
        return self.moment


def _service(
    session: Session,
    hasher: PasswordHasher,
    sender: CapturingEmailSender,
    clock: Clock | None = None,
) -> PasswordResetService:
    tokens = AuthTokenRepository(session)
    factory = TokenFactory()
    resolved_clock = clock or _FakeClock(_BASE)
    finalizer = CredentialResetFinalizer(SessionRepository(session), tokens, resolved_clock)
    return PasswordResetService(
        UserRepository(session),
        InstitutionRepository(session),
        TokenIssuer(tokens, factory),
        TokenConsumer(tokens, factory),
        hasher,
        sender,
        AuthSettings(),
        EmailSettings(),
        resolved_clock,
        finalizer,
        AuditLogger(AuditLogRepository(session)),
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
            institution_id=DEFAULT_INSTITUTION_ID,
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


def test_repeated_request_is_throttled(db_session: Session) -> None:
    hasher = PasswordHasher()
    sender = CapturingEmailSender()
    _seed_active_user(db_session, hasher)
    clock = _FakeClock(_BASE)
    service = _service(db_session, hasher, sender, clock)

    service.request("m@example.com")
    assert sender.reset_link is not None
    sender.reset_link = None

    service.request("m@example.com")
    assert sender.reset_link is None

    clock.moment = _BASE + timedelta(minutes=AuthSettings().reset_request_interval_minutes + 1)
    service.request("m@example.com")
    assert sender.reset_link is not None


def test_request_reaches_every_institution_holding_the_address(
    db_session: Session, seed_institution: Callable[..., Institution]
) -> None:
    hasher = PasswordHasher()
    other = seed_institution("מוסד אחר", "other")
    _seed_active_user(db_session, hasher)
    db_session.add(
        User(
            full_name="Manager",
            email="m@example.com",
            username="manager2",
            password_hash=hasher.hash("old-password"),
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            institution_id=other.id,
        )
    )
    db_session.flush()
    sender = CapturingEmailSender()

    _service(db_session, hasher, sender).request("m@example.com")

    assert sorted(message.username for message in sender.reset_messages) == [
        "manager1",
        "manager2",
    ]
    assert sorted(message.institution_name for message in sender.reset_messages) == [
        "מוסד אחר",
        "מוסד בדיקה",
    ]
    assert len({message.link for message in sender.reset_messages}) == 2


def test_request_names_the_institution_and_username_in_the_message(
    db_session: Session,
) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    sender = CapturingEmailSender()

    _service(db_session, hasher, sender).request("m@example.com")

    message = sender.reset_messages[0]
    assert message.username == "manager1"
    assert message.institution_name == "מוסד בדיקה"
