import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]

_BODY = {
    "national_id": "123456789",
    "date_of_birth": "2012-05-01",
    "home_language": "עברית",
    "medical_diagnoses": [{"name": "ADHD"}],
    "emergency_contacts": [{"full_name": "Mom", "phone": "050"}],
    "legal_status": "guardian_appointed",
    "guardians": [{"full_name": "Guardian", "relationship": "aunt"}],
}


def _seed_class(session: Session, name: str) -> uuid.UUID:
    entity = ClassEntity(name=name)
    session.add(entity)
    session.flush()
    return entity.id


def _seed_student(session: Session, class_id: uuid.UUID) -> uuid.UUID:
    student = Student(full_name="Dana", class_id=class_id)
    session.add(student)
    session.flush()
    return student.id


def test_manager_upserts_and_reads_full_details(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    student_id = _seed_student(db_session, class_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    put = api.put(f"/students/{student_id}/details", headers=headers, json=_BODY)
    assert put.status_code == 200
    assert put.json()["legal_status"] == "guardian_appointed"
    assert put.json()["age"] is not None

    got = api.get(f"/students/{student_id}/details", headers=headers)
    assert got.status_code == 200
    assert got.json()["guardians"][0]["full_name"] == "Guardian"
    assert got.json()["sensitive_visible"] is True


def test_professional_teacher_reads_without_sensitive_and_cannot_write(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    student_id = _seed_student(db_session, class_id)
    seed_user("boss", UserRole.MANAGER)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    api.put(
        f"/students/{student_id}/details",
        headers=auth_headers(api, "boss"),
        json=_BODY,
    )
    prof_headers = auth_headers(api, "prof")

    got = api.get(f"/students/{student_id}/details", headers=prof_headers)
    assert got.status_code == 200
    assert got.json()["legal_status"] is None
    assert got.json()["guardians"] == []
    assert got.json()["sensitive_visible"] is False
    assert got.json()["emergency_contacts"][0]["full_name"] == "Mom"

    forbidden = api.put(f"/students/{student_id}/details", headers=prof_headers, json=_BODY)
    assert forbidden.status_code == 403


def test_instructor_cannot_write_other_class_details(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    student_id = _seed_student(db_session, class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    headers = auth_headers(api, "teacher")

    response = api.put(f"/students/{student_id}/details", headers=headers, json=_BODY)
    assert response.status_code == 404


def test_details_require_authentication(api: TestClient, db_session: Session) -> None:
    class_id = _seed_class(db_session, "Aleph")
    student_id = _seed_student(db_session, class_id)

    assert api.get(f"/students/{student_id}/details").status_code == 401
