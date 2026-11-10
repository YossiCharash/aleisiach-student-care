import uuid
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def _body(responsible: list[str] | None = None, nature: str = "אוכל מהר") -> dict[str, Any]:
    return {
        "assessment_date": "2026-09-01",
        "items": [
            {
                "domain": "eating_drinking_swallowing",
                "nature": nature,
                "level": "medium",
                "intervention_plan": "השגחה",
                "responsible_user_ids": responsible or [],
            }
        ],
    }


def _url(student_id: uuid.UUID, suffix: str = "") -> str:
    return f"/students/{student_id}/risk-assessments{suffix}"


def _create(
    api: TestClient, student_id: uuid.UUID, headers: dict[str, str], body: dict[str, Any]
) -> dict[str, Any]:
    response = api.post(_url(student_id), headers=headers, json=body)
    assert response.status_code == 201
    created: dict[str, Any] = response.json()
    return created


def test_manager_creates_reads_updates_and_archives(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"), full_name="Noa")
    boss = seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    entry = _create(api, student_id, headers, _body([str(boss.id)]))
    first = entry["items"][0]
    assert first["level"] == "medium"
    assert first["responsible"] == [{"id": str(boss.id), "full_name": boss.full_name}]

    history = api.get(_url(student_id), headers=headers).json()
    assert history["student_name"] == "Noa"
    assert len(history["domains"]) == len(entry["items"])
    assert [item["id"] for item in history["entries"]] == [entry["id"]]

    updated = api.put(
        _url(student_id, f"/{entry['id']}"), headers=headers, json=_body(nature="חנק")
    )
    assert updated.status_code == 200
    assert updated.json()["items"][0]["nature"] == "חנק"

    archived = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)
    assert archived.status_code == 200
    assert api.get(_url(student_id), headers=headers).json()["entries"] == []


def test_unknown_level_or_responsible_is_rejected(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    bad_level = _body()
    bad_level["items"][0]["level"] = "extreme"

    level = api.post(_url(student_id), headers=headers, json=bad_level)
    responsible = api.post(_url(student_id), headers=headers, json=_body([str(uuid.uuid4())]))

    assert level.status_code == 422
    assert responsible.status_code == 422
    assert responsible.json()["code"] == "invalid_responsible_user"


def test_instructor_writes_own_workshop_and_lists_candidates_but_cannot_archive(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    teacher = seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    headers = auth_headers(api, "teacher")

    candidates = api.get(_url(student_id, "/responsible-candidates"), headers=headers)
    entry = _create(api, student_id, headers, _body([str(teacher.id)]))
    archive = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)

    assert candidates.status_code == 200
    assert str(teacher.id) in [member["id"] for member in candidates.json()]
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
    assert api.post(_url(student_id), headers=headers, json=_body()).status_code == 404


def test_professional_teacher_reads_but_cannot_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    entry = _create(api, student_id, auth_headers(api, "boss"), _body())
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(_url(student_id), headers=headers).status_code == 200
    assert api.post(_url(student_id), headers=headers, json=_body()).status_code == 403
    put = api.put(_url(student_id, f"/{entry['id']}"), headers=headers, json=_body())
    assert put.status_code == 403
    candidates = api.get(_url(student_id, "/responsible-candidates"), headers=headers)
    assert candidates.status_code == 403


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
    entry = _create(api, student_id, headers, _body())

    single = api.get(_url(student_id, f"/{entry['id']}/pdf"), headers=headers)
    assert single.status_code == 200
    assert single.headers["content-type"] == "application/pdf"
    assert quote("ניהול סיכונים.pdf", safe="") in single.headers["content-disposition"]

    combined = api.get(_url(student_id, "/pdf"), headers=headers)
    assert combined.status_code == 200
    assert quote("טבלאות ניהול סיכונים.pdf", safe="") in combined.headers["content-disposition"]


def test_assessments_require_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))

    assert api.get(_url(student_id)).status_code == 401
