import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.classes.class_repository import ClassRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.schema.routes.class_create_request import ClassCreateRequest
from backend.app.schema.routes.class_update_request import ClassUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.classes.class_service import ClassService


def _service(session: Session) -> ClassService:
    return ClassService(ClassRepository(session), AuditLogger(AuditLogRepository(session)))


def test_create_persists_and_audits(db_session: Session) -> None:
    actor_id = uuid.uuid4()
    service = _service(db_session)

    created = service.create(ClassCreateRequest(name="Aleph"), actor_id)

    assert created.name == "Aleph"
    log = db_session.scalars(select(AuditLog)).one()
    assert log.action == AuditAction.CREATE
    assert log.entity_type == "class"
    assert log.entity_id == created.id
    assert log.actor_id == actor_id


def test_list_all_sorted_by_name(db_session: Session) -> None:
    actor_id = uuid.uuid4()
    service = _service(db_session)
    service.create(ClassCreateRequest(name="Bet"), actor_id)
    service.create(ClassCreateRequest(name="Aleph"), actor_id)

    assert [entity.name for entity in service.list_all()] == ["Aleph", "Bet"]


def test_rename_updates_and_audits(db_session: Session) -> None:
    actor_id = uuid.uuid4()
    service = _service(db_session)
    created = service.create(ClassCreateRequest(name="Aleph"), actor_id)

    renamed = service.rename(created.id, ClassUpdateRequest(name="Gimel"), actor_id)

    assert renamed.name == "Gimel"
    actions = db_session.scalars(select(AuditLog.action)).all()
    assert AuditAction.UPDATE in actions


def test_rename_unknown_class_raises(db_session: Session) -> None:
    service = _service(db_session)

    with pytest.raises(NotFoundError):
        service.rename(uuid.uuid4(), ClassUpdateRequest(name="Gimel"), uuid.uuid4())
