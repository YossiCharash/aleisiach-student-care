import uuid
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_BODY = {
    "report_date": "2026-09-01",
    "general_background": "רקע כללי",
    "vocational_domain": "תחום תעסוקתי",
    "behavioral_emotional_domain": "תחום רגשי",
    "communication_social_domain": "תחום תקשורתי",
    "independence_life_skills_domain": "עצמאות",
    "summary_recommendations": "סיכום",
}


def _url(student_id: uuid.UUID, suffix: str = "") -> str:
    return f"/students/{student_id}/functional-report{suffix}"


def _create(api: TestClient, student_id: uuid.UUID, headers: dict[str, str]) -> dict[str, Any]:
    response = api.post(_url(student_id), headers=headers, json=_BODY)
    assert response.status_code == 201
    created: dict[str, Any] = response.json()
    return created


def test_manager_creates_reads_updates_and_archives(
    api: TestClient,
    db_session: Session,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"), full_name="Noa")
    db_session.add(StudentDetails(student_id=student_id, national_id="123456782"))
    db_session.flush()
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    entry = _create(api, student_id, headers)
    assert entry["report_date"] == "2026-09-01"
    assert entry["general_background"] == "רקע כללי"
    assert entry["author_name"] == "User"

    history = api.get(_url(student_id), headers=headers).json()
    assert history["student_name"] == "Noa"
    assert history["national_id"] == "123456782"
    assert [item["id"] for item in history["entries"]] == [entry["id"]]

    updated = api.patch(
        _url(student_id, f"/{entry['id']}"),
        headers=headers,
        json={"general_background": "מעודכן"},
    )
    assert updated.status_code == 200
    assert updated.json()["general_background"] == "מעודכן"
    assert updated.json()["report_date"] == "2026-09-01"

    archived = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)
    assert archived.status_code == 200
    assert api.get(_url(student_id), headers=headers).json()["entries"] == []


def test_each_save_adds_a_dated_entry_to_history(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    api.post(_url(student_id), headers=headers, json={**_BODY, "report_date": "2026-01-01"})
    api.post(_url(student_id), headers=headers, json={**_BODY, "report_date": "2026-06-01"})

    entries = api.get(_url(student_id), headers=headers).json()["entries"]
    assert [item["report_date"] for item in entries] == ["2026-06-01", "2026-01-01"]


def test_empty_report_is_rejected(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)

    response = api.post(
        _url(student_id), headers=auth_headers(api, "boss"), json={"report_date": "2026-09-01"}
    )

    assert response.status_code == 422


def test_instructor_reads_own_workshop_but_cannot_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("boss", UserRole.MANAGER)
    entry = _create(api, student_id, auth_headers(api, "boss"))
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    headers = auth_headers(api, "teacher")

    assert api.get(_url(student_id), headers=headers).status_code == 200
    assert api.post(_url(student_id), headers=headers, json=_BODY).status_code == 403
    patch = api.patch(
        _url(student_id, f"/{entry['id']}"), headers=headers, json={"general_background": "x"}
    )
    assert patch.status_code == 403
    archive = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)
    assert archive.status_code == 403


def test_professional_teacher_reads_but_cannot_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(_url(student_id), headers=headers).status_code == 200
    assert api.post(_url(student_id), headers=headers, json=_BODY).status_code == 403


def test_instructor_cannot_read_other_workshop(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_a = seed_workshop("Aleph")
    student_id = seed_student(seed_workshop("Bet"))
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=class_a)

    response = api.get(_url(student_id), headers=auth_headers(api, "teacher"))

    assert response.status_code == 404


def test_single_and_combined_pdf_export(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    entry = _create(api, student_id, headers)

    single = api.get(_url(student_id, f"/{entry['id']}/pdf"), headers=headers)
    assert single.status_code == 200
    assert single.headers["content-type"] == "application/pdf"
    assert quote("דוח תפקודי.pdf", safe="") in single.headers["content-disposition"]

    combined = api.get(_url(student_id, "/pdf"), headers=headers)
    assert combined.status_code == 200
    assert quote("דוחות תפקודיים.pdf", safe="") in combined.headers["content-disposition"]


def test_pdf_of_unknown_entry_is_not_found(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)

    response = api.get(_url(student_id, f"/{uuid.uuid4()}/pdf"), headers=auth_headers(api, "boss"))

    assert response.status_code == 404


def test_report_requires_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))

    assert api.get(_url(student_id)).status_code == 401
