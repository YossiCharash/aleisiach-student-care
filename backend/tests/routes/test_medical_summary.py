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
    "summary_date": "2026-11-01",
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


def test_manager_creates_and_lists(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"), full_name="Noa")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post(_url(student_id), headers=headers, json=_BODY)
    assert created.status_code == 201
    payload = created.json()
    assert payload["summary_date"] == "2026-11-01"
    assert payload["mobility"] == ["escort", "aids"]
    assert payload["author_name"] == "User"

    history = api.get(_url(student_id), headers=headers).json()
    assert history["student_name"] == "Noa"
    assert [entry["id"] for entry in history["entries"]] == [payload["id"]]
    assert history["entries"][0]["epilepsy_last_seizure"] == "2026-10-01"


def test_new_summary_is_added_to_history(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    api.post(_url(student_id), headers=headers, json=_BODY)
    api.post(_url(student_id), headers=headers, json={**_BODY, "summary_date": "2026-11-09"})

    entries = api.get(_url(student_id), headers=headers).json()["entries"]

    assert [entry["summary_date"] for entry in entries] == ["2026-11-09", "2026-11-01"]


def test_empty_history(
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
    assert got.json()["entries"] == []


def test_update_and_archive(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    entry_id = api.post(_url(student_id), headers=headers, json=_BODY).json()["id"]

    updated = api.put(_url(student_id, f"/{entry_id}"), headers=headers, json={"loves": "ציור"})
    assert updated.status_code == 200
    assert updated.json()["loves"] == "ציור"
    assert updated.json()["summary_date"] == "2026-11-01"

    archived = api.post(_url(student_id, f"/{entry_id}/archive"), headers=headers)
    assert archived.status_code == 200
    assert api.get(_url(student_id), headers=headers).json()["entries"] == []
    assert api.get(_url(student_id, f"/{entry_id}/pdf"), headers=headers).status_code == 404


def test_unknown_option_is_rejected(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)

    created = api.post(
        _url(student_id),
        headers=auth_headers(api, "boss"),
        json={**_BODY, "mobility": ["flying"]},
    )

    assert created.status_code == 422


def test_create_requires_a_date(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)

    created = api.post(_url(student_id), headers=auth_headers(api, "boss"), json={"allergies": "x"})

    assert created.status_code == 422


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
    assert api.post(_url(student_id), headers=headers, json=_BODY).status_code == 403
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
    assert api.post(_url(student_id), headers=headers, json=_BODY).status_code == 403


def test_per_entry_and_combined_pdf(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    entry_id = api.post(_url(student_id), headers=headers, json=_BODY).json()["id"]

    single = api.get(_url(student_id, f"/{entry_id}/pdf"), headers=headers)
    combined = api.get(_url(student_id, "/pdf"), headers=headers)

    assert single.status_code == 200
    assert single.headers["content-type"] == "application/pdf"
    assert combined.status_code == 200
    assert combined.headers["content-type"] == "application/pdf"


def test_requires_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    student_id = seed_student(seed_workshop("Aleph"))

    assert api.get(_url(student_id)).status_code == 401
