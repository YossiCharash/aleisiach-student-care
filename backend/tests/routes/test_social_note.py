import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_BODY = {"note_date": "2026-09-01", "content": "שיחה עם ההורים"}


def test_manager_creates_reads_updates_and_archives(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post(f"/students/{student_id}/social-note", headers=headers, json=_BODY)
    assert created.status_code == 201
    entry = created.json()
    assert entry["content"] == "שיחה עם ההורים"
    assert entry["note_date"] == "2026-09-01"
    assert entry["author_name"] == "User"

    report = api.get(f"/students/{student_id}/social-note", headers=headers)
    assert report.status_code == 200
    assert [item["id"] for item in report.json()["entries"]] == [entry["id"]]

    updated = api.patch(
        f"/students/{student_id}/social-note/{entry['id']}",
        headers=headers,
        json={"content": "מעודכן"},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == "מעודכן"

    archived = api.post(
        f"/students/{student_id}/social-note/{entry['id']}/archive", headers=headers
    )
    assert archived.status_code == 200

    after = api.get(f"/students/{student_id}/social-note", headers=headers)
    assert after.json()["entries"] == []


def test_instructor_reads_own_workshop_but_cannot_create(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("boss", UserRole.MANAGER)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    api.post(
        f"/students/{student_id}/social-note",
        headers=auth_headers(api, "boss"),
        json=_BODY,
    )
    teacher_headers = auth_headers(api, "teacher")

    got = api.get(f"/students/{student_id}/social-note", headers=teacher_headers)
    assert got.status_code == 200
    assert got.json()["entries"][0]["content"] == "שיחה עם ההורים"

    write = api.post(f"/students/{student_id}/social-note", headers=teacher_headers, json=_BODY)
    assert write.status_code == 403


def test_instructor_cannot_read_other_workshop_note(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_a = seed_workshop("Aleph")
    class_b = seed_workshop("Bet")
    student_id = seed_student(class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=class_a)
    headers = auth_headers(api, "teacher")

    assert api.get(f"/students/{student_id}/social-note", headers=headers).status_code == 404


def test_professional_teacher_is_blocked(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(f"/students/{student_id}/social-note", headers=headers).status_code == 403
    assert (
        api.post(f"/students/{student_id}/social-note", headers=headers, json=_BODY).status_code
        == 403
    )


def test_pdf_export_for_combined_and_single_entry(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    entry_id = api.post(
        f"/students/{student_id}/social-note", headers=headers, json=_BODY
    ).json()["id"]

    combined = api.get(f"/students/{student_id}/social-note/pdf", headers=headers)
    assert combined.status_code == 200
    assert combined.headers["content-type"] == "application/pdf"

    single = api.get(f"/students/{student_id}/social-note/{entry_id}/pdf", headers=headers)
    assert single.status_code == 200
    assert single.headers["content-type"] == "application/pdf"


def test_note_requires_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)

    assert api.get(f"/students/{student_id}/social-note").status_code == 401
