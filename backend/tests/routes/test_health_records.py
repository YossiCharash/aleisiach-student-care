import uuid
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.tests.support.seeding import seed_health_domains

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_DOMAINS: dict[str, str] = {}


@pytest.fixture(autouse=True)
def _health_domains(db_session: Session) -> None:
    physio, occupational = seed_health_domains(db_session)
    _DOMAINS["physio"] = str(physio.id)
    _DOMAINS["occupational"] = str(occupational.id)


def _body(
    responsible: list[str] | None = None,
    support: str = "תרגול הליכה",
    domain: str = "physio",
) -> dict[str, Any]:
    return {
        "domain_id": _DOMAINS[domain],
        "record_date": "2026-09-01",
        "session_type": "individual",
        "support_given": support,
        "responsible_user_ids": responsible or [],
        "notes": "שיתף פעולה",
        "execution_review": "בוצע",
    }


def _url(student_id: uuid.UUID, suffix: str = "") -> str:
    return f"/students/{student_id}/health-records{suffix}"


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
    assert entry["session_type"] == "individual"
    assert entry["responsible"] == [{"id": str(boss.id), "full_name": boss.full_name}]

    history = api.get(_url(student_id), headers=headers).json()
    assert history["student_name"] == "Noa"
    assert len(history["domains"]) == 2
    assert [item["id"] for item in history["entries"]] == [entry["id"]]

    updated = api.put(
        _url(student_id, f"/{entry['id']}"),
        headers=headers,
        json=_body(support="תרגול מדרגות", domain="occupational"),
    )
    assert updated.status_code == 200
    assert updated.json()["support_given"] == "תרגול מדרגות"
    assert updated.json()["domain_id"] == _DOMAINS["occupational"]

    archived = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)
    assert archived.status_code == 200
    assert api.get(_url(student_id), headers=headers).json()["entries"] == []


def test_empty_row_unknown_domain_and_foreign_responsible_are_rejected(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    empty = {"domain_id": _DOMAINS["physio"], "record_date": "2026-09-01"}
    unknown = {**_body(), "domain_id": str(uuid.uuid4())}

    assert api.post(_url(student_id), headers=headers, json=empty).status_code == 422
    domain = api.post(_url(student_id), headers=headers, json=unknown)
    responsible = api.post(_url(student_id), headers=headers, json=_body([str(uuid.uuid4())]))

    assert domain.json()["code"] == "invalid_health_domain"
    assert responsible.json()["code"] == "invalid_responsible_user"


def test_instructor_writes_own_workshop_but_cannot_archive(
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


def test_professional_teacher_writes_any_student_but_cannot_archive(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    entry = _create(api, student_id, headers, _body())
    put = api.put(_url(student_id, f"/{entry['id']}"), headers=headers, json=_body(support="x"))
    archive = api.post(_url(student_id, f"/{entry['id']}/archive"), headers=headers)

    assert put.status_code == 200
    assert archive.status_code == 403


def test_combined_and_per_domain_pdf_export(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    _create(api, student_id, headers, _body())

    combined = api.get(_url(student_id, "/pdf"), headers=headers)
    assert combined.status_code == 200
    assert combined.headers["content-type"] == "application/pdf"
    title = quote("תיעוד אישי – מקצועות הבריאות.pdf", safe="")
    assert title in combined.headers["content-disposition"]

    single = api.get(_url(student_id, f"/pdf?domain_id={_DOMAINS['physio']}"), headers=headers)
    assert single.status_code == 200
    assert quote("פיזיותרפיה.pdf", safe="") in single.headers["content-disposition"]


def test_domains_are_managed_by_managers_only(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    boss = auth_headers(api, "boss")
    prof = auth_headers(api, "prof")

    created = api.post("/health-domains", headers=boss, json={"name": "קלינאות תקשורת"})
    assert created.status_code == 201
    domain_id = created.json()["id"]
    deactivated = api.patch(f"/health-domains/{domain_id}", headers=boss, json={"is_active": False})
    assert deactivated.json()["is_active"] is False

    assert api.get("/health-domains", headers=prof).status_code == 200
    assert api.post("/health-domains", headers=prof, json={"name": "x"}).status_code == 403


def test_records_require_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))

    assert api.get(_url(student_id)).status_code == 401
