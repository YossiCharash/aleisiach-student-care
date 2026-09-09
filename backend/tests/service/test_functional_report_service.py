import uuid
from datetime import date

import pytest
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
from backend.app.schema.routes.functional_report_upsert_request import (
    FunctionalReportUpsertRequest,
)
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.functional_report_service import FunctionalReportService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request() -> FunctionalReportUpsertRequest:
    return FunctionalReportUpsertRequest(
        general_background="רקע",
        vocational_domain="תעסוקה",
        behavioral_emotional_domain="רגשי",
        communication_social_domain="תקשורת",
        independence_life_skills_domain="עצמאות",
        summary_recommendations="המלצות",
    )


def _setup(session: Session) -> tuple[FunctionalReportService, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    session.flush()
    session.add(
        StudentDetails(
            student_id=student.id, national_id="123456782", date_of_birth=date(2010, 5, 1)
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
    return service, student.id, seed_actor(session)


def test_upsert_then_get_roundtrip(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    saved = service.upsert(student_id, _request(), _ALL, actor)

    assert saved.exists is True
    assert saved.general_background == "רקע"
    assert saved.summary_recommendations == "המלצות"
    assert saved.written_by_name == "Actor"
    assert saved.updated_at is not None

    fetched = service.get(student_id, _ALL)
    assert fetched.vocational_domain == "תעסוקה"


def test_identity_is_auto_filled_from_student_and_details(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    response = service.get(student_id, _ALL)

    assert response.exists is False
    assert response.student_name == "Dana"
    assert response.national_id == "123456782"
    assert response.date_of_birth == date(2010, 5, 1)
    assert response.general_background == ""


def test_update_replaces_sections(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    service.upsert(student_id, _request(), _ALL, actor)

    updated = service.upsert(
        student_id,
        FunctionalReportUpsertRequest(general_background="חדש"),
        _ALL,
        actor,
    )

    assert updated.general_background == "חדש"
    assert updated.summary_recommendations == ""


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.get(student_id, foreign)


def test_upsert_is_audited_create_then_update(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    service.upsert(student_id, _request(), _ALL, actor)
    service.upsert(student_id, _request(), _ALL, actor)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [AuditAction.CREATE, AuditAction.UPDATE]
    assert all(log.entity_type == "functional_report" for log in logs)
    assert all(log.entity_id == student_id for log in logs)
    assert all("summary_recommendations" in log.changes for log in logs)
