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
from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.medical_summary_service import MedicalSummaryService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request() -> MedicalSummaryFields:
    return MedicalSummaryFields(
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


def test_upsert_then_get_roundtrip(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    saved = service.upsert(student_id, _request(), _ALL, actor)

    assert saved.exists is True
    assert saved.mobility == ["escort", "aids"]
    assert saved.epilepsy_known is True
    fetched = service.get(student_id, _ALL)
    assert fetched.allergies == "בוטנים"
    assert fetched.epilepsy_last_seizure == date(2026, 10, 1)
    assert fetched.written_by_name is not None


def test_identity_is_filled_from_student_details(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)

    response = service.get(student_id, _ALL)

    assert response.exists is False
    assert response.student_name == "Dana"
    assert response.national_id == "123456782"
    assert response.date_of_birth == date(2000, 5, 1)
    assert response.address == "רחוב הגפן 3"


def test_update_replaces_fields(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)
    service.upsert(student_id, _request(), _ALL, actor)

    updated = service.upsert(student_id, MedicalSummaryFields(loves="ציור"), _ALL, actor)

    assert updated.loves == "ציור"
    assert updated.allergies == ""
    assert updated.mobility == []
    assert updated.epilepsy_known is None


def test_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id, _ = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.get(student_id, foreign)


def test_audit_records_create_then_only_changed_fields(db_session: Session) -> None:
    service, student_id, actor = _setup(db_session)

    service.upsert(student_id, _request(), _ALL, actor)
    service.upsert(student_id, _request().model_copy(update={"allergies": "חלב"}), _ALL, actor)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [AuditAction.CREATE, AuditAction.UPDATE]
    assert all(log.entity_type == "medical_summary" for log in logs)
    assert "mobility" in logs[0].changes
    assert logs[1].changes == ["allergies"]
