import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.credential_reset_finalizer import CredentialResetFinalizer
from backend.app.service.auth.password_change_service import PasswordChangeService
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher

_CURRENT = "current-password"


def _service(session: Session, hasher: PasswordHasher) -> PasswordChangeService:
    finalizer = CredentialResetFinalizer(
        SessionRepository(session), AuthTokenRepository(session), Clock()
    )
    return PasswordChangeService(
        UserRepository(session),
        hasher,
        finalizer,
        AuditLogger(AuditLogRepository(session)),
    )


def _seed(session: Session, hasher: PasswordHasher) -> User:
    user = User(
        full_name="User",
        email="user@example.com",
        username="user",
        password_hash=hasher.hash(_CURRENT),
        role=UserRole.INSTRUCTOR,
        status=UserStatus.ACTIVE,
    )
    session.add(user)
    session.flush()
    return user


def test_change_replaces_hash(db_session: Session) -> None:
    hasher = PasswordHasher()
    user = _seed(db_session, hasher)
    service = _service(db_session, hasher)

    service.change(user.id, _CURRENT, "brand-new-password")

    assert user.password_hash is not None
    assert hasher.verify(user.password_hash, "brand-new-password")
    assert not hasher.verify(user.password_hash, _CURRENT)


def test_wrong_current_password_raises(db_session: Session) -> None:
    hasher = PasswordHasher()
    user = _seed(db_session, hasher)
    service = _service(db_session, hasher)

    with pytest.raises(InvalidCurrentPasswordError):
        service.change(user.id, "not-the-current", "brand-new-password")


def test_unknown_user_raises(db_session: Session) -> None:
    hasher = PasswordHasher()
    service = _service(db_session, hasher)

    with pytest.raises(AuthenticationError):
        service.change(uuid.uuid4(), _CURRENT, "brand-new-password")
