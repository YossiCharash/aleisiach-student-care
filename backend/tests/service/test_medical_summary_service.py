import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.medical_summary_create_request import MedicalSummaryCreateRequest
from backend.app.schema.routes.medical_summary_request import MedicalSummaryRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.medical_summary_service import MedicalSummaryService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request(summary_date: date = date(2026, 11, 1)) -> MedicalSummaryCreateRequest:
    return MedicalSummaryCreateRequest(
        summary_date=summary_date,
        phone="050-0000000",
        lives_with=["parents"],
        allergies="בוטנים",
        epilepsy_known=True,
        epilepsy_last_seizure=date(2026, 10, 1),
        mobility=["escort", "aids"],
        filler_role="אחות",
    )


def _setup(session: Session) -> tuple[MedicalSummaryService, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    session.flush()
    session.add(
        StudentDetails(
            student_id=student.id,
            national_id="123456782",
            date_of_birth=date(2000, 5, 1),
            address="רחוב הגפן 3",
        )
    )
    session.flush()
    service = MedicalSummaryService(
        MedicalSummaryRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student.id, seed_actor(session)


def test_create_then_history_roundtrip(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    saved = service.create(student_id, _request(), _ALL, actor)

    assert saved.summary_date == date(2026, 11, 1)
    assert saved.mobility == ["escort", "aids"]
    assert saved.author_name is not None
    history = service.history(student_id, _ALL)
    assert [entry.id for entry in history.entries] == [saved.id]
    assert history.entries[0].allergies == "בוטנים"
    assert history.entries[0].epilepsy_last_seizure == date(2026, 10, 1)


def test_history_identity_is_filled_from_student_details(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)

    history = service.history(student_id, _ALL)

    assert history.entries == []
    assert history.student_name == "Dana"
    assert history.national_id == "123456782"
    assert history.date_of_birth == date(2000, 5, 1)
    assert history.address == "רחוב הגפן 3"


def test_new_summary_keeps_the_previous_one_in_history(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    first = service.create(student_id, _request(date(2026, 1, 1)), _ALL, actor)
    second = service.create(student_id, _request(date(2026, 6, 1)), _ALL, actor)

    history = service.history(student_id, _ALL)

    assert [entry.id for entry in history.entries] == [second.id, first.id]


def test_update_replaces_fields_and_keeps_the_date(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    saved = service.create(student_id, _request(), _ALL, actor)

    updated = service.update(student_id, saved.id, MedicalSummaryRequest(loves="ציור"), _ALL, actor)

    assert updated.loves == "ציור"
    assert updated.allergies == ""
    assert updated.mobility == []
    assert updated.epilepsy_known is None
    assert updated.summary_date == date(2026, 11, 1)


def test_archive_hides_the_entry(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    saved = service.create(student_id, _request(), _ALL, actor)

    service.archive(student_id, saved.id, _ALL, actor)

    assert service.history(student_id, _ALL).entries == []
    with pytest.raises(NotFoundError):
        service.entry_history(student_id, saved.id, _ALL)


def test_entry_of_another_student_is_not_found(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    student = db_session.get(Student, student_id)
    assert student is not None
    other = Student(full_name="Other", workshop_id=student.workshop_id)
    db_session.add(other)
    db_session.flush()
    foreign = service.create(other.id, _request(), _ALL, actor)

    with pytest.raises(NotFoundError):
        service.update(student_id, foreign.id, MedicalSummaryRequest(), _ALL, actor)


def test_entry_history_holds_only_that_entry(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    first = service.create(student_id, _request(date(2026, 1, 1)), _ALL, actor)
    service.create(student_id, _request(date(2026, 6, 1)), _ALL, actor)

    history = service.entry_history(student_id, first.id, _ALL)

    assert [entry.id for entry in history.entries] == [first.id]


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.history(student_id, foreign)


def test_audit_records_create_update_and_archive(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    saved = service.create(student_id, _request(), _ALL, actor)
    changed = MedicalSummaryRequest(**_request().model_dump(exclude={"summary_date"}))
    changed.allergies = "חלב"
    service.update(student_id, saved.id, changed, _ALL, actor)
    service.archive(student_id, saved.id, _ALL, actor)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [
        AuditAction.CREATE,
        AuditAction.UPDATE,
        AuditAction.ARCHIVE,
    ]
    assert all(log.entity_type == "medical_summary" for log in logs)
    assert all(log.entity_id == saved.id for log in logs)
    assert "summary_date" in logs[0].changes
    assert logs[1].changes == ["allergies"]
