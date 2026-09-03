import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.classes.class_repository import ClassRepository
from backend.app.errors.service.class_not_empty_error import ClassNotEmptyError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.class_create_request import ClassCreateRequest
from backend.app.schema.routes.class_update_request import ClassUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.classes.class_service import ClassService
from backend.tests.conftest import DEFAULT_INSTITUTION_ID

_ACTOR = uuid.uuid4()


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


def test_list_active_sorted_by_name(db_session: Session) -> None:
    actor_id = uuid.uuid4()
    service = _service(db_session)
    service.create(ClassCreateRequest(name="Bet"), actor_id)
    service.create(ClassCreateRequest(name="Aleph"), actor_id)

    assert [entity.name for entity in service.list_active()] == ["Aleph", "Bet"]


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


def test_archive_hides_class_from_the_active_list(db_session: Session) -> None:
    service = _service(db_session)
    kept = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)
    retired = service.create(ClassCreateRequest(name="Bet"), _ACTOR)

    service.archive(retired.id, _ACTOR)

    assert [entity.id for entity in service.list_active()] == [kept.id]
    assert [entity.id for entity in service.list_archived()] == [retired.id]


def test_restore_returns_class_to_the_active_list(db_session: Session) -> None:
    service = _service(db_session)
    entity = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)
    service.archive(entity.id, _ACTOR)

    service.restore(entity.id, _ACTOR)

    assert [row.id for row in service.list_active()] == [entity.id]
    assert service.list_archived() == []


def test_archive_is_blocked_while_active_students_are_assigned(db_session: Session) -> None:
    service = _service(db_session)
    entity = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)
    db_session.add(Student(full_name="Dana", class_id=entity.id))
    db_session.flush()

    with pytest.raises(ClassNotEmptyError):
        service.archive(entity.id, _ACTOR)


def test_archive_is_blocked_while_a_user_is_assigned(db_session: Session) -> None:
    service = _service(db_session)
    entity = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)
    db_session.add(
        User(
            full_name="Teacher",
            email="t@example.com",
            role=UserRole.INSTRUCTOR,
            class_id=entity.id,
            status=UserStatus.ACTIVE,
            institution_id=DEFAULT_INSTITUTION_ID,
        )
    )
    db_session.flush()

    with pytest.raises(ClassNotEmptyError):
        service.archive(entity.id, _ACTOR)


def test_archived_students_do_not_block_archiving(db_session: Session) -> None:
    service = _service(db_session)
    entity = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)
    db_session.add(Student(full_name="Gone", class_id=entity.id, is_archived=True))
    db_session.flush()

    service.archive(entity.id, _ACTOR)

    assert [row.id for row in service.list_archived()] == [entity.id]


def test_archive_and_restore_are_audited(db_session: Session) -> None:
    service = _service(db_session)
    entity = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)

    service.archive(entity.id, _ACTOR)
    service.restore(entity.id, _ACTOR)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-2].action == AuditAction.ARCHIVE
    assert logs[-2].changes == ["is_archived"]
    assert logs[-1].action == AuditAction.UPDATE
    assert logs[-1].changes == ["is_archived"]


def test_rename_still_audits_the_name_field(db_session: Session) -> None:
    service = _service(db_session)
    entity = service.create(ClassCreateRequest(name="Aleph"), _ACTOR)

    service.rename(entity.id, ClassUpdateRequest(name="Gimel"), _ACTOR)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].changes == ["name"]


def test_archive_unknown_class_raises(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        _service(db_session).archive(uuid.uuid4(), _ACTOR)
