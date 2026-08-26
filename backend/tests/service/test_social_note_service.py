import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.schema.routes.social_note_upsert_request import SocialNoteUpsertRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.notes.social_note_service import SocialNoteService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ALL = StudentAccessScope(all_classes=True)
_ACTOR = uuid.uuid4()


def _setup(session: Session) -> tuple[SocialNoteService, uuid.UUID]:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    service = SocialNoteService(
        SocialNoteRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student.id


def test_upsert_then_get_roundtrip(db_session: Session) -> None:
    service, student_id = _setup(db_session)

    saved = service.upsert(
        student_id, SocialNoteUpsertRequest(content="שיחה עם ההורים"), _ALL, _ACTOR
    )

    assert saved.content == "שיחה עם ההורים"
    assert saved.updated_by == _ACTOR
    assert saved.updated_at is not None

    fetched = service.get(student_id, _ALL)
    assert fetched.content == "שיחה עם ההורים"


def test_get_empty_note_returns_blank(db_session: Session) -> None:
    service, student_id = _setup(db_session)

    response = service.get(student_id, _ALL)

    assert response.student_id == student_id
    assert response.content is None
    assert response.updated_by is None


def test_update_replaces_content(db_session: Session) -> None:
    service, student_id = _setup(db_session)
    service.upsert(student_id, SocialNoteUpsertRequest(content="ראשון"), _ALL, _ACTOR)

    updated = service.upsert(student_id, SocialNoteUpsertRequest(content="שני"), _ALL, _ACTOR)

    assert updated.content == "שני"


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id = _setup(db_session)
    foreign = StudentAccessScope(all_classes=False, class_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.get(student_id, foreign)


def test_upsert_is_audited_create_then_update(db_session: Session) -> None:
    service, student_id = _setup(db_session)

    service.upsert(student_id, SocialNoteUpsertRequest(content="ראשון"), _ALL, _ACTOR)
    service.upsert(student_id, SocialNoteUpsertRequest(content="שני"), _ALL, _ACTOR)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [AuditAction.CREATE, AuditAction.UPDATE]
    assert all(log.entity_type == "social_note" for log in logs)
    assert all(log.entity_id == student_id for log in logs)
    assert all(log.changes == ["content"] for log in logs)
