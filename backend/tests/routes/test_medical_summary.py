import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_BODY = {
    "phone": "050-0000000",
    "lives_with": ["parents"],
    "allergies": "בוטנים",
    "epilepsy_known": True,
    "epilepsy_last_seizure": "2026-10-01",
    "mobility": ["escort", "aids"],
    "diet": ["other"],
    "diet_other": "ללא גלוטן",
    "loves": "מוזיקה",
    "filler_role": "אחות",
}


def _url(student_id: uuid.UUID, suffix: str = "") -> str:
    return f"/students/{student_id}/medical-summary{suffix}"


def test_manager_writes_and_reads(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"), full_name="Noa")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    put = api.put(_url(student_id), headers=headers, json=_BODY)
    assert put.status_code == 200
    payload = put.json()
    assert payload["exists"] is True
    assert payload["student_name"] == "Noa"
    assert payload["mobility"] == ["escort", "aids"]
    assert payload["epilepsy_known"] is True

    got = api.get(_url(student_id), headers=headers).json()
    assert got["allergies"] == "בוטנים"
    assert got["epilepsy_last_seizure"] == "2026-10-01"
    assert got["written_by_name"] == "User"


def test_get_before_write_returns_empty(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)

    got = api.get(_url(student_id), headers=auth_headers(api, "boss"))

    assert got.status_code == 200
    assert got.json()["exists"] is False
    assert got.json()["mobility"] == []


def test_unknown_option_is_rejected(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)

    put = api.put(
        _url(student_id), headers=auth_headers(api, "boss"), json={"mobility": ["flying"]}
    )

    assert put.status_code == 422


def test_instructor_cannot_read_or_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    headers = auth_headers(api, "teacher")

    assert api.get(_url(student_id), headers=headers).status_code == 403
    assert api.put(_url(student_id), headers=headers, json=_BODY).status_code == 403
    assert api.get(_url(student_id, "/pdf"), headers=headers).status_code == 403


def test_professional_teacher_cannot_read_or_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(_url(student_id), headers=headers).status_code == 403
    assert api.put(_url(student_id), headers=headers, json=_BODY).status_code == 403


def test_pdf_export(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    api.put(_url(student_id), headers=headers, json=_BODY)

    pdf = api.get(_url(student_id, "/pdf"), headers=headers)

    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"


def test_requires_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))

    assert api.get(_url(student_id)).status_code == 401
