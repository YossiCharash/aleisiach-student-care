from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedClass = Callable[..., object]
SeedStudent = Callable[..., object]

_BODY = {
    "national_id": "123456789",
    "date_of_birth": "2012-05-01",
    "home_language": "עברית",
    "medical_diagnoses": [{"name": "ADHD"}],
    "emergency_contacts": [{"full_name": "Mom", "phone": "050"}],
    "legal_status": "guardian_appointed",
    "guardians": [{"full_name": "Guardian", "relationship": "aunt"}],
}


def test_manager_upserts_and_reads_full_details(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)
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


def test_instructor_reads_and_writes_own_class_details(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)
    headers = auth_headers(api, "teacher")

    put = api.put(f"/students/{student_id}/details", headers=headers, json=_BODY)
    assert put.status_code == 200
    assert put.json()["legal_status"] == "guardian_appointed"

    got = api.get(f"/students/{student_id}/details", headers=headers)
    assert got.status_code == 200
    assert got.json()["guardians"][0]["full_name"] == "Guardian"
    assert got.json()["sensitive_visible"] is True


def test_professional_teacher_reads_without_sensitive_and_cannot_write(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)
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
    body = got.json()
    assert body["legal_status"] is None
    assert body["guardians"] == []
    assert body["sensitive_visible"] is False
    assert body["national_id"] == "123456789"
    assert body["medical_diagnoses"][0]["name"] == "ADHD"
    assert body["emergency_contacts"][0]["full_name"] == "Mom"

    forbidden = api.put(f"/students/{student_id}/details", headers=prof_headers, json=_BODY)
    assert forbidden.status_code == 403


def test_instructor_cannot_write_other_class_details(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_a = seed_class("Aleph")
    class_b = seed_class("Bet")
    student_id = seed_student(class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    headers = auth_headers(api, "teacher")

    response = api.put(f"/students/{student_id}/details", headers=headers, json=_BODY)
    assert response.status_code == 404


def test_details_require_authentication(
    api: TestClient, seed_class: SeedClass, seed_student: SeedStudent
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)

    assert api.get(f"/students/{student_id}/details").status_code == 401
