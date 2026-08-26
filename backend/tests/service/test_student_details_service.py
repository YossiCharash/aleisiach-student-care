import uuid
from datetime import date

import pytest
from sqlalchemy.orm import Session

from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.legal_status import LegalStatus
from backend.app.models.client.student import Student
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis
from backend.app.schema.routes.student_details_upsert_request import (
    StudentDetailsUpsertRequest,
)
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_details_service import StudentDetailsService
from backend.app.utils.service.age_calculator import AgeCalculator

_ALL = StudentAccessScope(all_classes=True)


def _setup(session: Session) -> tuple[StudentDetailsService, uuid.UUID]:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    service = StudentDetailsService(
        StudentDetailsRepository(session), StudentAccessGuard(StudentRepository(session))
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

    saved = service.upsert(student_id, request, _ALL)

    assert saved.national_id == "123456789"
    assert saved.age == AgeCalculator.age_in_years(date(2012, 5, 1), date.today())
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
    )

    updated = service.upsert(student_id, StudentDetailsUpsertRequest(national_id="222"), _ALL)

    assert updated.national_id == "222"
    assert updated.guardians == []


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
