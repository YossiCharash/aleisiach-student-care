import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.workshops.workshop_repository import WorkshopRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.errors.service.workshop_not_empty_error import WorkshopNotEmptyError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.workshop_create_request import WorkshopCreateRequest
from backend.app.schema.routes.workshop_update_request import WorkshopUpdateRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.workshops.workshop_service import WorkshopService
from backend.tests.conftest import DEFAULT_INSTITUTION_ID

_ACTOR = uuid.uuid4()
_ALL = StudentAccessScope(all_workshops=True)
_COLOR = "#3F8420"
_OTHER_COLOR = "#85C441"


def _service(session: Session) -> WorkshopService:
    return WorkshopService(WorkshopRepository(session), AuditLogger(AuditLogRepository(session)))


def _create(
    service: WorkshopService,
    name: str,
    color: str = _COLOR,
    instructor_id: uuid.UUID | None = None,
) -> uuid.UUID:
    request = WorkshopCreateRequest(name=name, color=color, instructor_id=instructor_id)
    return service.create(request, _ACTOR).id


def _add_instructor(session: Session, name: str) -> User:
    user = User(
        full_name=name,
        email=f"{uuid.uuid4().hex}@example.com",
        role=UserRole.INSTRUCTOR,
        status=UserStatus.ACTIVE,
        institution_id=DEFAULT_INSTITUTION_ID,
    )
    session.add(user)
    session.flush()
    return user


def test_create_persists_and_audits(db_session: Session) -> None:
    actor_id = uuid.uuid4()
    service = _service(db_session)

    created = service.create(WorkshopCreateRequest(name="Aleph", color=_COLOR), actor_id)

    assert created.name == "Aleph"
    assert created.color == _COLOR
    log = db_session.scalars(select(AuditLog)).one()
    assert log.action == AuditAction.CREATE
    assert log.entity_type == "workshop"
    assert log.entity_id == created.id
    assert log.actor_id == actor_id
    assert log.changes == ["name", "color"]


def test_list_active_sorted_by_name(db_session: Session) -> None:
    service = _service(db_session)
    _create(service, "Bet")
    _create(service, "Aleph")

    assert [entity.name for entity in service.list_active(_ALL)] == ["Aleph", "Bet"]


def test_instructor_scope_lists_only_its_own_workshop(db_session: Session) -> None:
    service = _service(db_session)
    own = _create(service, "Aleph")
    _create(service, "Bet")

    scope = StudentAccessScope(all_workshops=False, workshop_id=own)
    assert [entity.id for entity in service.list_active(scope)] == [own]


def test_update_changes_name_and_color(db_session: Session) -> None:
    service = _service(db_session)
    workshop_id = _create(service, "Aleph")

    updated = service.update(
        workshop_id, WorkshopUpdateRequest(name="Gimel", color=_OTHER_COLOR), _ACTOR
    )

    assert updated.name == "Gimel"
    assert updated.color == _OTHER_COLOR
    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].action == AuditAction.UPDATE
    assert logs[-1].changes == ["name", "color"]


def test_update_unknown_workshop_raises(db_session: Session) -> None:
    service = _service(db_session)

    with pytest.raises(NotFoundError):
        service.update(
            uuid.uuid4(), WorkshopUpdateRequest(name="Gimel", color=_COLOR), uuid.uuid4()
        )


def test_create_assigns_the_chosen_instructor(db_session: Session) -> None:
    service = _service(db_session)
    instructor = _add_instructor(db_session, "Dana")

    result = _create(service, "Aleph", instructor_id=instructor.id)

    db_session.refresh(instructor)
    assert instructor.workshop_id == result
    listed = service.list_active(_ALL)
    assert listed[0].instructor_id == instructor.id
    assert listed[0].instructor_name == "Dana"


def test_update_reassigns_instructor_and_frees_the_previous_one(db_session: Session) -> None:
    service = _service(db_session)
    first = _add_instructor(db_session, "First")
    second = _add_instructor(db_session, "Second")
    workshop_id = _create(service, "Aleph", instructor_id=first.id)

    service.update(
        workshop_id,
        WorkshopUpdateRequest(name="Aleph", color=_COLOR, instructor_id=second.id),
        _ACTOR,
    )

    db_session.refresh(first)
    db_session.refresh(second)
    assert first.workshop_id is None
    assert second.workshop_id == workshop_id


def test_clearing_instructor_frees_the_holder(db_session: Session) -> None:
    service = _service(db_session)
    instructor = _add_instructor(db_session, "Dana")
    workshop_id = _create(service, "Aleph", instructor_id=instructor.id)

    service.update(workshop_id, WorkshopUpdateRequest(name="Aleph", color=_COLOR), _ACTOR)

    db_session.refresh(instructor)
    assert instructor.workshop_id is None


def test_unknown_instructor_raises(db_session: Session) -> None:
    service = _service(db_session)

    with pytest.raises(NotFoundError):
        service.create(
            WorkshopCreateRequest(name="Aleph", color=_COLOR, instructor_id=uuid.uuid4()),
            _ACTOR,
        )


def test_disabled_instructor_cannot_be_assigned(db_session: Session) -> None:
    service = _service(db_session)
    instructor = _add_instructor(db_session, "Dana")
    instructor.status = UserStatus.DISABLED
    db_session.flush()

    with pytest.raises(NotFoundError):
        service.create(
            WorkshopCreateRequest(name="Aleph", color=_COLOR, instructor_id=instructor.id),
            _ACTOR,
        )


def test_archive_hides_workshop_from_the_active_list(db_session: Session) -> None:
    service = _service(db_session)
    kept = _create(service, "Aleph")
    retired = _create(service, "Bet")

    service.archive(retired, _ACTOR)

    assert [entity.id for entity in service.list_active(_ALL)] == [kept]
    assert [entity.id for entity in service.list_archived()] == [retired]


def test_restore_returns_workshop_to_the_active_list(db_session: Session) -> None:
    service = _service(db_session)
    workshop_id = _create(service, "Aleph")
    service.archive(workshop_id, _ACTOR)

    service.restore(workshop_id, _ACTOR)

    assert [row.id for row in service.list_active(_ALL)] == [workshop_id]
    assert service.list_archived() == []


def test_archive_is_blocked_while_active_students_are_assigned(db_session: Session) -> None:
    service = _service(db_session)
    workshop_id = _create(service, "Aleph")
    db_session.add(Student(full_name="Dana", workshop_id=workshop_id))
    db_session.flush()

    with pytest.raises(WorkshopNotEmptyError):
        service.archive(workshop_id, _ACTOR)


def test_archive_is_blocked_while_a_user_is_assigned(db_session: Session) -> None:
    service = _service(db_session)
    workshop_id = _create(service, "Aleph")
    db_session.add(
        User(
            full_name="Teacher",
            email="t@example.com",
            role=UserRole.INSTRUCTOR,
            workshop_id=workshop_id,
            status=UserStatus.ACTIVE,
            institution_id=DEFAULT_INSTITUTION_ID,
        )
    )
    db_session.flush()

    with pytest.raises(WorkshopNotEmptyError):
        service.archive(workshop_id, _ACTOR)


def test_archived_students_do_not_block_archiving(db_session: Session) -> None:
    service = _service(db_session)
    workshop_id = _create(service, "Aleph")
    db_session.add(Student(full_name="Gone", workshop_id=workshop_id, is_archived=True))
    db_session.flush()

    service.archive(workshop_id, _ACTOR)

    assert [row.id for row in service.list_archived()] == [workshop_id]


def test_archive_and_restore_are_audited(db_session: Session) -> None:
    service = _service(db_session)
    workshop_id = _create(service, "Aleph")

    service.archive(workshop_id, _ACTOR)
    service.restore(workshop_id, _ACTOR)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-2].action == AuditAction.ARCHIVE
    assert logs[-2].changes == ["is_archived"]
    assert logs[-1].action == AuditAction.UPDATE
    assert logs[-1].changes == ["is_archived"]


def test_archive_unknown_workshop_raises(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        _service(db_session).archive(uuid.uuid4(), _ACTOR)
