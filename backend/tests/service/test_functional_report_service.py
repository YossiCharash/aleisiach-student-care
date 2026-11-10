import uuid
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.functional_report_repository import FunctionalReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.functional_report_create_request import (
    FunctionalReportCreateRequest,
)
from backend.app.schema.routes.functional_report_update_request import (
    FunctionalReportUpdateRequest,
)
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.functional_report_service import FunctionalReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request(
    report_date: date = date(2026, 9, 1), background: str = "רקע"
) -> FunctionalReportCreateRequest:
    return FunctionalReportCreateRequest(
        report_date=report_date,
        general_background=background,
        vocational_domain="תעסוקה",
        summary_recommendations="המלצות",
    )


def _add_student(session: Session, workshop_id: uuid.UUID, name: str) -> uuid.UUID:
    student = Student(full_name=name, workshop_id=workshop_id)
    session.add(student)
    session.flush()
    return student.id


def _setup(session: Session) -> tuple[FunctionalReportService, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student_id = _add_student(session, workshop.id, "Dana")
    session.add(
        StudentDetails(
            student_id=student_id, national_id="123456782", date_of_birth=date(2010, 5, 1)
        )
    )
    session.flush()
    service = FunctionalReportService(
        FunctionalReportRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student_id, seed_actor(session)


def test_create_then_history_lists_entry(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    created = service.create(student_id, _request(), _ALL, actor)

    assert created.report_date == date(2026, 9, 1)
    assert created.general_background == "רקע"
    assert created.author_name == "Actor"
    history = service.history(student_id, _ALL)
    assert [entry.id for entry in history.entries] == [created.id]


def test_history_carries_identity_from_student_and_details(db_session: Session) -> None:
    service, student_id, _actor = _setup(db_session)

    history = service.history(student_id, _ALL)

    assert history.entries == []
    assert history.student_name == "Dana"
    assert history.national_id == "123456782"
    assert history.date_of_birth == date(2010, 5, 1)


def test_history_orders_newest_date_first(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    older = service.create(student_id, _request(date(2026, 1, 1), "ישן"), _ALL, actor)
    newer = service.create(student_id, _request(date(2026, 9, 1), "חדש"), _ALL, actor)

    history = service.history(student_id, _ALL)

    assert [entry.id for entry in history.entries] == [newer.id, older.id]


def test_update_replaces_sections_and_keeps_date(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)

    updated = service.update(
        student_id,
        created.id,
        FunctionalReportUpdateRequest(general_background="חדש"),
        _ALL,
        actor,
    )

    assert updated.general_background == "חדש"
    assert updated.summary_recommendations == ""
    assert updated.report_date == date(2026, 9, 1)


def test_archive_hides_entry(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)

    service.archive(student_id, created.id, _ALL, actor)

    assert service.history(student_id, _ALL).entries == []
    with pytest.raises(NotFoundError):
        service.entry_history(student_id, created.id, _ALL)


def test_entry_of_another_student_is_not_found(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)
    student = db_session.get(Student, student_id)
    assert student is not None
    other_id = _add_student(db_session, student.workshop_id, "Other")

    with pytest.raises(NotFoundError):
        service.entry_history(other_id, created.id, _ALL)


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id, _actor = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.history(student_id, foreign)


def test_changes_are_audited(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)
    service.update(
        student_id, created.id, FunctionalReportUpdateRequest(general_background="x"), _ALL, actor
    )
    service.archive(student_id, created.id, _ALL, actor)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [
        AuditAction.CREATE,
        AuditAction.UPDATE,
        AuditAction.ARCHIVE,
    ]
    assert all(log.entity_type == "functional_report" for log in logs)
    assert all(log.entity_id == created.id for log in logs)


def test_request_requires_at_least_one_section() -> None:
    with pytest.raises(ValidationError):
        FunctionalReportUpdateRequest(general_background="   ")
