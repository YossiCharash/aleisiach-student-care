import uuid
from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.errors.service.cannot_disable_self_error import CannotDisableSelfError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_update_request import UserUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher
from backend.app.service.auth.token_issuer import TokenIssuer
from backend.app.service.users.user_management_service import UserManagementService
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.service.capturing_email_sender import CapturingEmailSender

_ACTOR = uuid.uuid4()


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


def _service(session: Session, sender: CapturingEmailSender | None = None) -> UserManagementService:
    tokens = AuthTokenRepository(session)
    return UserManagementService(
        UserRepository(session),
        ClassRepository(session),
        InvitationDispatcher(
            tokens,
            TokenIssuer(tokens, TokenFactory()),
            sender or CapturingEmailSender(),
            AuthSettings(),
            EmailSettings(),
        ),
        AuditLogger(AuditLogRepository(session)),
    )


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


def test_changing_email_of_invited_user_resends_invitation(db_session: Session) -> None:
    sender = CapturingEmailSender()
    invited = _seed(db_session, "pending", status=UserStatus.INVITED, password_hash=None)
    service = _service(db_session, sender)

    service.update(
        invited.id,
        UserUpdateRequest(
            full_name="User",
            email="corrected@example.com",
            role=UserRole.PROFESSIONAL_TEACHER,
        ),
        _ACTOR,
    )

    assert sender.invitation_link is not None


def test_changing_email_of_active_user_does_not_resend_invitation(db_session: Session) -> None:
    sender = CapturingEmailSender()
    active = _seed(db_session, "working", role=UserRole.PROFESSIONAL_TEACHER)
    service = _service(db_session, sender)

    service.update(
        active.id,
        UserUpdateRequest(
            full_name="User",
            email="moved@example.com",
            role=UserRole.PROFESSIONAL_TEACHER,
        ),
        _ACTOR,
    )

    assert sender.invitation_link is None


def test_resent_invitation_invalidates_the_previous_token(db_session: Session) -> None:
    sender = CapturingEmailSender()
    invited = _seed(db_session, "pending", status=UserStatus.INVITED, password_hash=None)
    tokens = AuthTokenRepository(db_session)
    issuer = TokenIssuer(tokens, TokenFactory())
    stale_raw = issuer.issue(invited.id, TokenKind.INVITE, timedelta(hours=1))
    stale_hash = TokenFactory().hash_token(stale_raw)

    _service(db_session, sender).update(
        invited.id,
        UserUpdateRequest(
            full_name="User",
            email="corrected@example.com",
            role=UserRole.PROFESSIONAL_TEACHER,
        ),
        _ACTOR,
    )

    stale_token = tokens.find_by_hash(stale_hash)
    assert stale_token is not None
    assert stale_token.used_at is not None


def test_update_without_changes_is_not_audited(db_session: Session) -> None:
    user = _seed(db_session, "steady", role=UserRole.PROFESSIONAL_TEACHER)
    service = _service(db_session)
    before = len(list(db_session.scalars(select(AuditLog))))

    service.update(
        user.id,
        UserUpdateRequest(
            full_name=user.full_name,
            email=user.email,
            role=UserRole.PROFESSIONAL_TEACHER,
        ),
        _ACTOR,
    )

    assert len(list(db_session.scalars(select(AuditLog)))) == before
