import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder


def test_recorder_stamps_its_entity_type_on_every_entry(db_session: Session) -> None:
    recorder = EntityAuditRecorder(AuditLogger(AuditLogRepository(db_session)), "detail_option")
    actor = uuid.uuid4()
    entity = uuid.uuid4()

    recorder.record(actor, AuditAction.CREATE, entity, ["field", "name"])

    log = db_session.scalars(select(AuditLog)).one()
    assert log.entity_type == "detail_option"
    assert log.actor_id == actor
    assert log.action == AuditAction.CREATE
    assert log.entity_id == entity
    assert log.changes == ["field", "name"]


def test_two_recorders_keep_their_own_entity_type(db_session: Session) -> None:
    logger = AuditLogger(AuditLogRepository(db_session))
    users = EntityAuditRecorder(logger, "user")
    permissions = EntityAuditRecorder(logger, "permission")
    actor = uuid.uuid4()

    users.record(actor, AuditAction.UPDATE, uuid.uuid4(), ["role"])
    permissions.record(actor, AuditAction.ARCHIVE, uuid.uuid4(), ["status"])

    stored = db_session.scalars(select(AuditLog).order_by(AuditLog.entity_type)).all()
    assert [log.entity_type for log in stored] == ["permission", "user"]
