from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.authentication_service import AuthenticationService
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.tests.support.fake_clock import FakeClock

_BASE = datetime(2026, 8, 27, 9, 0, tzinfo=UTC)


class _CountingHasher(PasswordHasher):
    def __init__(self) -> None:
        super().__init__()
        self.dummy_calls = 0

    def verify_dummy(self, password: str) -> None:
        self.dummy_calls += 1
        super().verify_dummy(password)


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
    return AuthenticationService(
        UserRepository(session),
        hasher,
        AuthSettings(),
        clock,
        AuditLogger(AuditLogRepository(session)),
    )


def test_authenticate_success(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, FakeClock(_BASE))

    result = service.authenticate("manager1", "password123")

    assert result.username == "manager1"


def test_authenticate_wrong_password_raises(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, FakeClock(_BASE))

    with pytest.raises(AuthenticationError):
        service.authenticate("manager1", "wrong-password")


def test_authenticate_unknown_user_raises(db_session: Session) -> None:
    service = _service(db_session, PasswordHasher(), FakeClock(_BASE))

    with pytest.raises(AuthenticationError):
        service.authenticate("ghost", "password123")


def test_unknown_user_still_runs_a_verify_to_equalize_timing(db_session: Session) -> None:
    hasher = _CountingHasher()
    service = _service(db_session, hasher, FakeClock(_BASE))

    with pytest.raises(AuthenticationError):
        service.authenticate("ghost", "password123")

    assert hasher.dummy_calls == 1


def test_locks_after_max_failed_attempts(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, FakeClock(_BASE))

    for _ in range(AuthSettings().max_failed_logins):
        with pytest.raises(AuthenticationError):
            service.authenticate("manager1", "wrong-password")

    with pytest.raises(AuthenticationError):
        service.authenticate("manager1", "password123")


def test_lockout_expires_after_window(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    clock = FakeClock(_BASE)
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
    service = _service(db_session, hasher, FakeClock(_BASE))
    with pytest.raises(AuthenticationError):
        service.authenticate("manager1", "wrong-password")

    service.authenticate("manager1", "password123")

    user = UserRepository(db_session).get_by_username("manager1")
    assert user is not None
    assert user.failed_login_count == 0


def test_successful_login_is_audited_with_source_ip(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, FakeClock(_BASE))

    service.authenticate(
        "manager1", "password123", AuthEventContext(ip="203.0.113.7", user_agent="pytest")
    )

    logs = list(db_session.scalars(select(AuditLog)))
    login = [log for log in logs if log.action == AuditAction.LOGIN]
    assert len(login) == 1
    assert login[0].entity_type == "auth"
    assert login[0].ip == "203.0.113.7"
    assert login[0].user_agent == "pytest"


def test_lockout_is_audited(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = _service(db_session, hasher, FakeClock(_BASE))

    for _ in range(AuthSettings().max_failed_logins):
        with pytest.raises(AuthenticationError):
            service.authenticate("manager1", "wrong-password")

    actions = list(db_session.scalars(select(AuditLog.action)))
    assert AuditAction.LOGIN_FAILED in actions
    assert AuditAction.LOCKOUT in actions
