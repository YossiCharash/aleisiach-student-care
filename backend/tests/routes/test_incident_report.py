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

_BODY: dict[str, Any] = {
    "event_date": "2026-09-01",
    "event_time": "14:30",
    "location": "חדר האוכל",
    "reporter_name_role": "דנה, מדריכה",
    "report_type": "internal",
    "natures": ["violence", "other"],
    "nature_other": "צעקות",
    "description": "תיאור האירוע",
    "referrals": ["guardian"],
    "manager_updated_date": "2026-09-01",
    "manager_updated_time": "16:00",
    "filler_role": "מדריכה",
}


def _url(student_id: uuid.UUID, suffix: str = "") -> str:
    return f"/students/{student_id}/incident-reports{suffix}"


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
    assert entry["event_time"] == "14:30:00"
    assert entry["natures"] == ["violence", "other"]
    assert entry["report_type"] == "internal"

    history = api.get(_url(student_id), headers=headers).json()
    assert history["student_name"] == "Noa"
    assert history["national_id"] == "123456782"
    assert [item["id"] for item in history["entries"]] == [entry["id"]]

    updated = api.put(
        _url(student_id, f"/{entry['id']}"),
        headers=headers,
        json={**_BODY, "description": "מעודכן", "referrals": ["police"]},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "מעודכן"
    assert updated.json()["referrals"] == ["police"]

    archived = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)
    assert archived.status_code == 200
    assert api.get(_url(student_id), headers=headers).json()["entries"] == []


def test_history_is_newest_first(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    api.post(_url(student_id), headers=headers, json={**_BODY, "event_date": "2026-01-01"})
    api.post(_url(student_id), headers=headers, json={**_BODY, "event_date": "2026-06-01"})

    entries = api.get(_url(student_id), headers=headers).json()["entries"]
    assert [item["event_date"] for item in entries] == ["2026-06-01", "2026-01-01"]


def test_missing_description_or_unknown_choice_is_rejected(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    no_description = api.post(_url(student_id), headers=headers, json={**_BODY, "description": ""})
    unknown_nature = api.post(_url(student_id), headers=headers, json={**_BODY, "natures": ["x"]})

    assert no_description.status_code == 422
    assert unknown_nature.status_code == 422


def test_instructor_writes_own_workshop_but_cannot_archive(
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

    entry = _create(api, student_id, headers)
    updated = api.put(
        _url(student_id, f"/{entry['id']}"), headers=headers, json={**_BODY, "location": "חצר"}
    )
    archive = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)

    assert updated.status_code == 200
    assert archive.status_code == 403


def test_instructor_cannot_reach_other_workshop(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    own = seed_workshop("Aleph")
    student_id = seed_student(seed_workshop("Bet"))
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=own)
    headers = auth_headers(api, "teacher")

    assert api.get(_url(student_id), headers=headers).status_code == 404
    assert api.post(_url(student_id), headers=headers, json=_BODY).status_code == 404


def test_professional_teacher_reads_but_cannot_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    entry = _create(api, student_id, auth_headers(api, "boss"))
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(_url(student_id), headers=headers).status_code == 200
    assert api.post(_url(student_id), headers=headers, json=_BODY).status_code == 403
    put = api.put(_url(student_id, f"/{entry['id']}"), headers=headers, json=_BODY)
    assert put.status_code == 403


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
    assert quote("דוח אירוע חריג.pdf", safe="") in single.headers["content-disposition"]

    combined = api.get(_url(student_id, "/pdf"), headers=headers)
    assert combined.status_code == 200
    assert quote("דוחות אירוע חריג.pdf", safe="") in combined.headers["content-disposition"]


def test_pdf_of_unknown_report_is_not_found(
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


def test_reports_require_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))

    assert api.get(_url(student_id)).status_code == 401


def test_instructor_cannot_edit_or_archive_other_workshop_report(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    own = seed_workshop("Aleph")
    student_id = seed_student(seed_workshop("Bet"))
    seed_user("boss", UserRole.MANAGER)
    entry = _create(api, student_id, auth_headers(api, "boss"))
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=own)
    headers = auth_headers(api, "teacher")

    put = api.put(_url(student_id, f"/{entry['id']}"), headers=headers, json=_BODY)
    archive = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)

    assert put.status_code == 404
    assert archive.status_code == 403
