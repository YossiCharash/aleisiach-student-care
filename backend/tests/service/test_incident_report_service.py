import uuid
from datetime import date, time

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.incident_report_repository import IncidentReportRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.incident_nature import IncidentNature
from backend.app.models.client.incident_referral import IncidentReferral
from backend.app.models.client.incident_report_type import IncidentReportType
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.incident_report_request import IncidentReportRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.incident_report_service import IncidentReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request(
    event_date: date = date(2026, 9, 1), description: str = "תיאור האירוע"
) -> IncidentReportRequest:
    return IncidentReportRequest(
        event_date=event_date,
        event_time=time(10, 15),
        location="חדר האוכל",
        report_type=IncidentReportType.INTERNAL,
        natures=[IncidentNature.VIOLENCE],
        description=description,
        referrals=[IncidentReferral.GUARDIAN, IncidentReferral.POLICE],
    )


def _setup(session: Session) -> tuple[IncidentReportService, uuid.UUID, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    session.flush()
    session.add(StudentDetails(student_id=student.id, national_id="123456782"))
    session.flush()
    service = IncidentReportService(
        IncidentReportRepository(session),
        StudentDetailsRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student.id, workshop.id, seed_actor(session)


def test_create_then_history_lists_report_with_identity(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)

    created = service.create(student_id, _request(), _ALL, actor)
    history = service.history(student_id, _ALL)

    assert history.student_name == "Dana"
    assert history.national_id == "123456782"
    assert [entry.id for entry in history.entries] == [created.id]
    entry = history.entries[0]
    assert entry.event_time == time(10, 15)
    assert entry.natures == [IncidentNature.VIOLENCE]
    assert entry.referrals == [IncidentReferral.GUARDIAN, IncidentReferral.POLICE]
    assert entry.author_name == "Actor"


def test_update_replaces_fields_and_keeps_author(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)
    editor = seed_actor(db_session, "editor")

    updated = service.update(
        student_id, created.id, _request(date(2026, 9, 2), "מעודכן"), _ALL, editor
    )

    assert updated.description == "מעודכן"
    assert updated.event_date == date(2026, 9, 2)
    assert updated.author_id == actor


def test_archive_hides_report_and_audits(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)

    service.archive(student_id, created.id, _ALL, actor)

    assert service.history(student_id, _ALL).entries == []
    actions = db_session.scalars(
        select(AuditLog.action).where(AuditLog.entity_type == "incident_report")
    ).all()
    assert list(actions) == [AuditAction.CREATE, AuditAction.ARCHIVE]


def test_audit_records_field_names_not_values(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)

    service.create(student_id, _request(), _ALL, actor)

    log = db_session.scalars(select(AuditLog)).one()
    assert "description" in log.changes
    assert "תיאור האירוע" not in log.changes


def test_entry_history_of_another_student_is_not_found(db_session: Session) -> None:
    service, student_id, workshop_id, actor = _setup(db_session)
    other = Student(full_name="Other", workshop_id=workshop_id)
    db_session.add(other)
    db_session.flush()
    created = service.create(student_id, _request(), _ALL, actor)

    with pytest.raises(NotFoundError):
        service.entry_history(other.id, created.id, _ALL)


def test_instructor_scope_outside_workshop_is_not_found(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    foreign_scope = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.create(student_id, _request(), foreign_scope, actor)


def test_request_requires_description() -> None:
    with pytest.raises(ValidationError):
        IncidentReportRequest(event_date=date(2026, 9, 1), description="  ")


def test_request_deduplicates_choices() -> None:
    request = IncidentReportRequest(
        event_date=date(2026, 9, 1),
        description="x",
        natures=[IncidentNature.VIOLENCE, IncidentNature.VIOLENCE],
    )

    assert request.natures == [IncidentNature.VIOLENCE]


def test_update_audits_only_changed_fields(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)
    edited = _request().model_copy(update={"location": "חצר"})

    service.update(student_id, created.id, edited, _ALL, actor)

    update_log = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.UPDATE)
    ).one()
    assert update_log.changes == ["location"]


def test_other_text_is_dropped_when_other_is_not_chosen() -> None:
    request = IncidentReportRequest(
        event_date=date(2026, 9, 1),
        description="x",
        natures=[IncidentNature.VIOLENCE],
        nature_other="ישן",
        referrals=[IncidentReferral.OTHER],
        referral_other="עירייה",
    )

    assert request.nature_other == ""
    assert request.referral_other == "עירייה"
