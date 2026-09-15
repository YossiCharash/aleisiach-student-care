import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.supported_employment_repository import (
    SupportedEmploymentRepository,
)
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.supported_employment_upsert_request import (
    SupportedEmploymentUpsertRequest,
)
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.supported_employment_service import SupportedEmploymentService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request() -> SupportedEmploymentUpsertRequest:
    return SupportedEmploymentUpsertRequest(
        workplace="מאפייה מרכזית",
        address="רחוב הפרחים 5",
        activity_type="אריזה",
        work_process="אריזת מאפים",
        work_environment="מטבח תעשייתי",
        required_body_functions="עמידה ממושכת",
        hazards_and_safety="תנור חם",
        workplace_contact="דנה",
        escort_contact="יוסי",
        mobility="הסעה מאורגנת",
        work_hours="08:00-14:00",
    )


def _setup(session: Session) -> tuple[SupportedEmploymentService, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    session.flush()
    service = SupportedEmploymentService(
        SupportedEmploymentRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student.id, seed_actor(session)


def test_upsert_then_get_roundtrip(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    saved = service.upsert(student_id, _request(), _ALL, actor)

    assert saved.exists is True
    assert saved.workplace == "מאפייה מרכזית"
    assert saved.work_hours == "08:00-14:00"

    fetched = service.get(student_id, _ALL)
    assert fetched.hazards_and_safety == "תנור חם"
    assert fetched.mobility == "הסעה מאורגנת"


def test_get_before_write_returns_empty(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)

    response = service.get(student_id, _ALL)

    assert response.exists is False
    assert response.student_id == student_id
    assert response.workplace == ""


def test_update_replaces_fields(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    service.upsert(student_id, _request(), _ALL, actor)

    updated = service.upsert(
        student_id,
        SupportedEmploymentUpsertRequest(workplace="מקום חדש"),
        _ALL,
        actor,
    )

    assert updated.workplace == "מקום חדש"
    assert updated.address == ""
    assert updated.work_hours == ""


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.get(student_id, foreign)


def test_upsert_is_audited_create_then_update(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    service.upsert(student_id, _request(), _ALL, actor)
    service.upsert(student_id, _request(), _ALL, actor)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [AuditAction.CREATE, AuditAction.UPDATE]
    assert all(log.entity_type == "supported_employment" for log in logs)
    assert all(log.entity_id == student_id for log in logs)
    assert all("workplace" in log.changes for log in logs)
