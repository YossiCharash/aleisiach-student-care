import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.social_note_create_request import SocialNoteCreateRequest
from backend.app.schema.routes.social_note_update_request import SocialNoteUpdateRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.notes.social_note_service import SocialNoteService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _setup(session: Session) -> tuple[SocialNoteService, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    session.flush()
    service = SocialNoteService(
        SocialNoteRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student.id, seed_actor(session)


def _create(
    service: SocialNoteService,
    student_id: uuid.UUID,
    actor: uuid.UUID,
    note_date: date,
    content: str,
) -> uuid.UUID:
    entry = service.create(
        student_id, SocialNoteCreateRequest(note_date=note_date, content=content), _ALL, actor
    )
    return entry.id


def test_create_then_report_lists_entry(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    created = service.create(
        student_id,
        SocialNoteCreateRequest(note_date=date(2026, 9, 1), content="שיחה עם ההורים"),
        _ALL,
        actor,
    )

    assert created.content == "שיחה עם ההורים"
    assert created.author_id == actor
    assert created.author_name == "Actor"

    report = service.report(student_id, _ALL)
    assert report.student_name == "Dana"
    assert [entry.id for entry in report.entries] == [created.id]


def test_report_orders_newest_date_first(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    older = _create(service, student_id, actor, date(2026, 1, 1), "ישן")
    newer = _create(service, student_id, actor, date(2026, 9, 1), "חדש")

    report = service.report(student_id, _ALL)

    assert [entry.id for entry in report.entries] == [newer, older]


def test_empty_report_has_no_entries(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)

    report = service.report(student_id, _ALL)

    assert report.entries == []
    assert report.student_name == "Dana"


def test_update_replaces_content_keeps_date(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    entry_id = _create(service, student_id, actor, date(2026, 5, 5), "ראשון")

    updated = service.update(
        student_id, entry_id, SocialNoteUpdateRequest(content="מעודכן"), _ALL, actor
    )

    assert updated.content == "מעודכן"
    assert updated.note_date == date(2026, 5, 5)


def test_archive_hides_entry_from_report(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    kept = _create(service, student_id, actor, date(2026, 2, 2), "נשמר")
    removed = _create(service, student_id, actor, date(2026, 3, 3), "יימחק")

    service.archive(student_id, removed, _ALL, actor)

    report = service.report(student_id, _ALL)
    assert [entry.id for entry in report.entries] == [kept]


def test_update_archived_entry_raises_not_found(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    entry_id = _create(service, student_id, actor, date(2026, 4, 4), "הערה")
    service.archive(student_id, entry_id, _ALL, actor)

    with pytest.raises(NotFoundError):
        service.update(student_id, entry_id, SocialNoteUpdateRequest(content="x"), _ALL, actor)


def test_missing_entry_raises_not_found(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    with pytest.raises(NotFoundError):
        service.update(
            student_id, uuid.uuid4(), SocialNoteUpdateRequest(content="x"), _ALL, actor
        )


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.report(student_id, foreign)


def test_audit_records_create_update_archive(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    entry_id = _create(service, student_id, actor, date(2026, 6, 6), "ראשון")
    service.update(student_id, entry_id, SocialNoteUpdateRequest(content="שני"), _ALL, actor)
    service.archive(student_id, entry_id, _ALL, actor)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [
        AuditAction.CREATE,
        AuditAction.UPDATE,
        AuditAction.ARCHIVE,
    ]
    assert all(log.entity_type == "social_note" for log in logs)
    assert all(log.entity_id == entry_id for log in logs)
