import uuid
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger
from backend.tests.conftest import DEFAULT_INSTITUTION_ID


def test_record_persists_entry(db_session: Session) -> None:
    logger = AuditLogger(AuditLogRepository(db_session))
    actor = uuid.uuid4()
    entity = uuid.uuid4()

    logger.record(
        AuditEntry(
            actor_id=actor,
            action=AuditAction.UPDATE,
            entity_type="student_details",
            entity_id=entity,
            changes=["national_id", "legal_status"],
        )
    )

    log = db_session.scalars(select(AuditLog)).one()
    assert log.actor_id == actor
    assert log.action == AuditAction.UPDATE
    assert log.entity_type == "student_details"
    assert log.entity_id == entity
    assert log.changes == ["national_id", "legal_status"]
    assert log.created_at is not None


def test_entry_falls_back_to_the_actor_institution_when_unbound(
    db_session: Session, seed_user: Callable[..., User]
) -> None:
    actor = seed_user("boss", UserRole.MANAGER)

    with TenantBinding.platform(db_session):
        AuditLogger(AuditLogRepository(db_session)).record(
            AuditEntry(
                actor_id=actor.id,
                action=AuditAction.LOGIN,
                entity_type="auth",
                entity_id=actor.id,
            )
        )
        stored = db_session.scalars(select(AuditLog)).one()

    assert stored.institution_id == DEFAULT_INSTITUTION_ID


def test_entry_of_a_platform_actor_has_no_institution(
    db_session: Session, seed_user: Callable[..., User]
) -> None:
    actor = seed_user("root", UserRole.SUPER_ADMIN)

    with TenantBinding.platform(db_session):
        AuditLogger(AuditLogRepository(db_session)).record(
            AuditEntry(
                actor_id=actor.id,
                action=AuditAction.LOGIN,
                entity_type="auth",
                entity_id=actor.id,
            )
        )
        stored = db_session.scalars(select(AuditLog)).one()

    assert stored.institution_id is None
