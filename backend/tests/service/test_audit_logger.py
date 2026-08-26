import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger


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
