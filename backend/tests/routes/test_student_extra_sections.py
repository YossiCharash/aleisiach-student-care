import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedClass = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def _seed_type(api: TestClient, headers: dict[str, str], name: str) -> str:
    section_id: str = api.post("/extra-section-types", headers=headers, json={"name": name}).json()[
        "id"
    ]
    return section_id


def test_manager_sets_and_reads_student_section(
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
    type_id = _seed_type(api, headers, "רקע חינוכי")

    put = api.put(
        f"/students/{student_id}/extra-sections/{type_id}",
        headers=headers,
        json={"content": "למד בבית ספר יסודי X"},
    )
    assert put.status_code == 200
    assert put.json()["content"] == "למד בבית ספר יסודי X"

    got = api.get(f"/students/{student_id}/extra-sections", headers=headers)
    assert got.status_code == 200
    entries = {row["section_type_id"]: row for row in got.json()}
    assert entries[type_id]["content"] == "למד בבית ספר יסודי X"
    assert entries[type_id]["name"] == "רקע חינוכי"


def test_professional_teacher_reads_but_cannot_write(
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
    type_id = _seed_type(api, auth_headers(api, "boss"), "העדפות")
    prof_headers = auth_headers(api, "prof")

    assert (
        api.get(f"/students/{student_id}/extra-sections", headers=prof_headers).status_code == 200
    )
    forbidden = api.put(
        f"/students/{student_id}/extra-sections/{type_id}",
        headers=prof_headers,
        json={"content": "x"},
    )
    assert forbidden.status_code == 403


def test_instructor_cannot_write_other_class(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_a = seed_class("Aleph")
    class_b = seed_class("Bet")
    student_id = seed_student(class_b)
    seed_user("boss", UserRole.MANAGER)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    type_id = _seed_type(api, auth_headers(api, "boss"), "העדפות")

    response = api.put(
        f"/students/{student_id}/extra-sections/{type_id}",
        headers=auth_headers(api, "teacher"),
        json={"content": "x"},
    )
    assert response.status_code == 404


def test_sections_require_authentication(
    api: TestClient, seed_class: SeedClass, seed_student: SeedStudent
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id)

    assert api.get(f"/students/{student_id}/extra-sections").status_code == 401
