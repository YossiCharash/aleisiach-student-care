import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.cannot_disable_self_error import CannotDisableSelfError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.users.user_management_service import UserManagementService


def _seed(
    session: Session,
    username: str,
    role: UserRole = UserRole.INSTRUCTOR,
    status: UserStatus = UserStatus.ACTIVE,
    password_hash: str | None = "hashed-password",
) -> User:
    user = User(
        full_name="User",
        email=f"{username}@example.com",
        username=username,
        role=role,
        status=status,
        password_hash=password_hash,
    )
    session.add(user)
    session.flush()
    return user


def _service(session: Session) -> UserManagementService:
    return UserManagementService(UserRepository(session), AuditLogger(AuditLogRepository(session)))


def test_list_users_returns_all(db_session: Session) -> None:
    _seed(db_session, "a")
    _seed(db_session, "b")
    service = _service(db_session)

    assert len(service.list_users()) == 2


def test_disable_sets_status_and_audits(db_session: Session) -> None:
    actor = _seed(db_session, "boss", UserRole.MANAGER)
    target = _seed(db_session, "teacher")
    service = _service(db_session)

    result = service.disable(target.id, actor.id)

    assert result.status == UserStatus.DISABLED
    log = db_session.scalars(select(AuditLog)).one()
    assert log.action == AuditAction.ARCHIVE
    assert log.entity_type == "permission"
    assert log.entity_id == target.id
    assert log.actor_id == actor.id


def test_cannot_disable_self(db_session: Session) -> None:
    actor = _seed(db_session, "boss", UserRole.MANAGER)
    service = _service(db_session)

    with pytest.raises(CannotDisableSelfError):
        service.disable(actor.id, actor.id)


def test_disable_unknown_user_raises(db_session: Session) -> None:
    actor = _seed(db_session, "boss", UserRole.MANAGER)
    service = _service(db_session)

    with pytest.raises(NotFoundError):
        service.disable(uuid.uuid4(), actor.id)


def test_enable_reactivates(db_session: Session) -> None:
    actor = _seed(db_session, "boss", UserRole.MANAGER)
    target = _seed(db_session, "teacher", status=UserStatus.DISABLED)
    service = _service(db_session)

    result = service.enable(target.id, actor.id)

    assert result.status == UserStatus.ACTIVE


def test_enable_keeps_uninitialised_account_invited(db_session: Session) -> None:
    actor = _seed(db_session, "boss", UserRole.MANAGER)
    target = _seed(db_session, "invitee", status=UserStatus.INVITED, password_hash=None)
    service = _service(db_session)

    result = service.enable(target.id, actor.id)

    assert result.status == UserStatus.INVITED
