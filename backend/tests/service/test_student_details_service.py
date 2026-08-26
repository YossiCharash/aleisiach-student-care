import uuid
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.legal_status import LegalStatus
from backend.app.models.client.student import Student
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis
from backend.app.schema.routes.student_details_upsert_request import (
    StudentDetailsUpsertRequest,
)
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_details_service import StudentDetailsService
from backend.app.utils.service.clock import Clock

_ALL = StudentAccessScope(all_classes=True)
_TODAY = date(2026, 8, 26)
_ACTOR = uuid.uuid4()


class _FixedClock(Clock):
    def today(self) -> date:
        return _TODAY

    def now(self) -> datetime:
        return datetime(2026, 8, 26, tzinfo=UTC)


def _setup(session: Session) -> tuple[StudentDetailsService, uuid.UUID]:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    service = StudentDetailsService(
        StudentDetailsRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        _FixedClock(),
    )
    return service, student.id


def test_upsert_then_get_roundtrip(db_session: Session) -> None:
    service, student_id = _setup(db_session)
    request = StudentDetailsUpsertRequest(
        national_id="123456789",
        date_of_birth=date(2012, 5, 1),
        home_language="עברית",
        medical_diagnoses=[Diagnosis(name="ADHD", notes="mild")],
        emergency_contacts=[ContactInfo(full_name="Mom", phone="050")],
        legal_status=LegalStatus.GUARDIAN_APPOINTED,
        guardians=[ContactInfo(full_name="Guardian", relationship="aunt")],
    )

    saved = service.upsert(student_id, request, _ALL, _ACTOR)

    assert saved.national_id == "123456789"
    assert saved.age == 14
    assert saved.legal_status == LegalStatus.GUARDIAN_APPOINTED
    assert saved.guardians[0].full_name == "Guardian"

    fetched = service.get(student_id, _ALL, include_sensitive=True)
    assert fetched.national_id == "123456789"
    assert fetched.medical_diagnoses[0].name == "ADHD"
    assert fetched.emergency_contacts[0].full_name == "Mom"


def test_upsert_replaces_previous_values(db_session: Session) -> None:
    service, student_id = _setup(db_session)
    service.upsert(
        student_id,
        StudentDetailsUpsertRequest(national_id="111", guardians=[ContactInfo(full_name="A")]),
        _ALL,
        _ACTOR,
    )

    updated = service.upsert(
        student_id, StudentDetailsUpsertRequest(national_id="222"), _ALL, _ACTOR
    )

    assert updated.national_id == "222"
    assert updated.guardians == []


def test_upsert_records_audit_entry_with_field_names_only(db_session: Session) -> None:
    service, student_id = _setup(db_session)

    service.upsert(
        student_id,
        StudentDetailsUpsertRequest(national_id="123", legal_status=LegalStatus.GUARDIAN_APPOINTED),
        _ALL,
        _ACTOR,
    )
    service.upsert(student_id, StudentDetailsUpsertRequest(national_id="456"), _ALL, _ACTOR)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at, AuditLog.action)))
    actions = {log.action for log in logs}
    assert AuditAction.CREATE in actions
    assert AuditAction.UPDATE in actions
    create_log = next(log for log in logs if log.action == AuditAction.CREATE)
    assert create_log.actor_id == _ACTOR
    assert create_log.entity_type == "student_details"
    assert create_log.entity_id == student_id
    assert set(create_log.changes) == {"national_id", "legal_status"}
    assert "123" not in create_log.changes


def test_get_hides_sensitive_when_not_permitted(db_session: Session) -> None:
    service, student_id = _setup(db_session)
    service.upsert(
        student_id,
        StudentDetailsUpsertRequest(
            legal_status=LegalStatus.PARENTS_ARE_GUARDIANS,
            guardians=[ContactInfo(full_name="Guardian")],
            emergency_contacts=[ContactInfo(full_name="Emergency")],
        ),
        _ALL,
        _ACTOR,
    )

    hidden = service.get(student_id, _ALL, include_sensitive=False)

    assert hidden.legal_status is None
    assert hidden.guardians == []
    assert hidden.sensitive_visible is False
    assert hidden.emergency_contacts[0].full_name == "Emergency"


def test_get_empty_details_returns_blank(db_session: Session) -> None:
    service, student_id = _setup(db_session)

    response = service.get(student_id, _ALL, include_sensitive=True)

    assert response.student_id == student_id
    assert response.national_id is None
    assert response.guardians == []
    assert response.age is None


def test_get_for_out_of_scope_student_is_hidden(db_session: Session) -> None:
    service, student_id = _setup(db_session)
    foreign = StudentAccessScope(all_classes=False, class_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.get(student_id, foreign, include_sensitive=True)
