import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedClass = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_BODY = {"content": "שיחה עם ההורים"}


def test_manager_writes_and_reads_note(
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

    put = api.put(f"/students/{student_id}/social-note", headers=headers, json=_BODY)
    assert put.status_code == 200
    assert put.json()["content"] == "שיחה עם ההורים"

    got = api.get(f"/students/{student_id}/social-note", headers=headers)
    assert got.status_code == 200
    assert got.json()["content"] == "שיחה עם ההורים"


def test_instructor_reads_own_class_but_cannot_write(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)
    seed_user("boss", UserRole.MANAGER)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)
    api.put(
        f"/students/{student_id}/social-note",
        headers=auth_headers(api, "boss"),
        json=_BODY,
    )
    teacher_headers = auth_headers(api, "teacher")

    got = api.get(f"/students/{student_id}/social-note", headers=teacher_headers)
    assert got.status_code == 200
    assert got.json()["content"] == "שיחה עם ההורים"

    write = api.put(f"/students/{student_id}/social-note", headers=teacher_headers, json=_BODY)
    assert write.status_code == 403


def test_instructor_cannot_read_other_class_note(
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

    assert api.get(f"/students/{student_id}/social-note", headers=headers).status_code == 404


def test_professional_teacher_is_blocked(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(f"/students/{student_id}/social-note", headers=headers).status_code == 403
    assert (
        api.put(f"/students/{student_id}/social-note", headers=headers, json=_BODY).status_code
        == 403
    )


def test_note_requires_authentication(
    api: TestClient, seed_class: SeedClass, seed_student: SeedStudent
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)

    assert api.get(f"/students/{student_id}/social-note").status_code == 401
