import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.errors.service.email_already_used_error import EmailAlreadyUsedError
from backend.app.errors.service.invalid_token_error import InvalidTokenError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.service.invitation_command import InvitationCommand
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher
from backend.app.service.auth.invitation_service import InvitationService
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.service.auth.token_issuer import TokenIssuer
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.service.capturing_email_sender import CapturingEmailSender

_ACTOR = uuid.uuid4()


def _service(session: Session, sender: CapturingEmailSender) -> InvitationService:
    tokens = AuthTokenRepository(session)
    factory = TokenFactory()
    return InvitationService(
        UserRepository(session),
        InvitationDispatcher(
            tokens,
            TokenIssuer(tokens, factory),
            sender,
            AuthSettings(),
            EmailSettings(),
        ),
        TokenConsumer(tokens, factory),
        PasswordHasher(),
        AuditLogger(AuditLogRepository(session)),
    )


def test_invite_then_accept_activates_user(db_session: Session) -> None:
    sender = CapturingEmailSender()
    service = _service(db_session, sender)

    invited = service.invite(
        InvitationCommand(full_name="Manager", email="m@example.com", role=UserRole.MANAGER),
        _ACTOR,
    )
    assert invited.status == UserStatus.INVITED
    assert sender.invitation_link is not None

    token = CapturingEmailSender.token_from(sender.invitation_link)
    activated = service.accept(token, "manager1", "manager-pass-2026")

    assert activated.status == UserStatus.ACTIVE
    assert activated.username == "manager1"


def test_invite_records_permission_audit(db_session: Session) -> None:
    service = _service(db_session, CapturingEmailSender())

    invited = service.invite(
        InvitationCommand(full_name="Teacher", email="t@example.com", role=UserRole.INSTRUCTOR),
        _ACTOR,
    )

    log = db_session.scalars(select(AuditLog)).one()
    assert log.action == AuditAction.CREATE
    assert log.entity_type == "permission"
    assert log.entity_id == invited.id
    assert log.actor_id == _ACTOR
    assert "role" in log.changes


def test_invite_duplicate_email_raises(db_session: Session) -> None:
    service = _service(db_session, CapturingEmailSender())
    command = InvitationCommand(full_name="M", email="dup@example.com", role=UserRole.MANAGER)
    service.invite(command, _ACTOR)

    with pytest.raises(EmailAlreadyUsedError):
        service.invite(command, _ACTOR)


@pytest.mark.parametrize("status", [UserStatus.DISABLED, UserStatus.ACTIVE])
def test_accept_is_refused_for_a_user_who_is_no_longer_invited(
    db_session: Session, status: UserStatus
) -> None:
    sender = CapturingEmailSender()
    service = _service(db_session, sender)
    invited = service.invite(
        InvitationCommand(full_name="Manager", email="m@example.com", role=UserRole.MANAGER),
        _ACTOR,
    )
    assert sender.invitation_link is not None
    token = CapturingEmailSender.token_from(sender.invitation_link)
    user = UserRepository(db_session).get(invited.id)
    assert user is not None
    user.status = status
    db_session.flush()

    with pytest.raises(InvalidTokenError):
        service.accept(token, "manager1", "manager-pass-2026")

    assert user.username is None
    assert user.password_hash is None
    assert user.status is status


def test_accept_with_unknown_token_raises(db_session: Session) -> None:
    service = _service(db_session, CapturingEmailSender())

    with pytest.raises(InvalidTokenError):
        service.accept("not-a-real-token", "someone", "manager-pass-2026")
