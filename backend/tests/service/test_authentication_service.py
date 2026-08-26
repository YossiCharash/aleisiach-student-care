from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.errors.service.account_locked_error import AccountLockedError
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.service.auth.authentication_service import AuthenticationService
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher

_BASE = datetime(2026, 8, 27, 9, 0, tzinfo=UTC)


class _FakeClock(Clock):
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def now(self) -> datetime:
        return self.moment


def _seed_active_user(session: Session, hasher: PasswordHasher) -> None:
    session.add(
        User(
            full_name="Manager",
            email="m@example.com",
            username="manager1",
            password_hash=hasher.hash("password123"),
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
    )
    session.flush()


def _service(session: Session, hasher: PasswordHasher, clock: Clock) -> AuthenticationService:
    return AuthenticationService(UserRepository(session), hasher, AuthSettings(), clock)


def test_authenticate_success(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, _FakeClock(_BASE))

    result = service.authenticate("manager1", "password123")

    assert result.username == "manager1"


def test_authenticate_wrong_password_raises(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, _FakeClock(_BASE))

    with pytest.raises(AuthenticationError):
        service.authenticate("manager1", "wrong-password")


def test_authenticate_unknown_user_raises(db_session: Session) -> None:
    service = _service(db_session, PasswordHasher(), _FakeClock(_BASE))

    with pytest.raises(AuthenticationError):
        service.authenticate("ghost", "password123")


def test_locks_after_max_failed_attempts(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, _FakeClock(_BASE))

    for _ in range(AuthSettings().max_failed_logins):
        with pytest.raises(AuthenticationError):
            service.authenticate("manager1", "wrong-password")

    with pytest.raises(AccountLockedError):
        service.authenticate("manager1", "password123")


def test_lockout_expires_after_window(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    clock = _FakeClock(_BASE)
    service = _service(db_session, hasher, clock)
    for _ in range(AuthSettings().max_failed_logins):
        with pytest.raises(AuthenticationError):
            service.authenticate("manager1", "wrong-password")

    clock.moment = _BASE + timedelta(minutes=AuthSettings().lockout_minutes + 1)
    result = service.authenticate("manager1", "password123")

    assert result.username == "manager1"


def test_success_resets_failed_count(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, _FakeClock(_BASE))
    with pytest.raises(AuthenticationError):
        service.authenticate("manager1", "wrong-password")

    service.authenticate("manager1", "password123")

    user = UserRepository(db_session).get_by_username("manager1")
    assert user is not None
    assert user.failed_login_count == 0
