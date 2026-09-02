import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedClass = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def test_manager_archives_and_restores_an_empty_class(
    api: TestClient, seed_class: SeedClass, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = seed_class("Bet")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    archived = api.post(f"/classes/{class_id}/archive", headers=headers)
    assert archived.status_code == 200

    assert api.get("/classes", headers=headers).json() == []
    assert [row["id"] for row in api.get("/classes/archived", headers=headers).json()] == [
        str(class_id)
    ]

    restored = api.post(f"/classes/{class_id}/restore", headers=headers)
    assert restored.status_code == 200
    assert [row["id"] for row in api.get("/classes", headers=headers).json()] == [str(class_id)]


def test_archiving_a_class_with_students_returns_409(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    seed_student(class_id, "Dana")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/classes/{class_id}/archive", headers=headers)

    assert response.status_code == 409
    assert response.json()["code"] == "class_not_empty"


def test_archived_class_cannot_receive_a_new_student(
    api: TestClient, seed_class: SeedClass, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = seed_class("Bet")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    api.post(f"/classes/{class_id}/archive", headers=headers)

    response = api.post(
        "/students",
        json={"full_name": "Newcomer", "class_id": str(class_id)},
        headers=headers,
    )

    assert response.status_code == 404


def test_archived_class_cannot_be_assigned_to_a_user(
    api: TestClient, seed_class: SeedClass, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = seed_class("Bet")
    prof_id = seed_user("prof", UserRole.PROFESSIONAL_TEACHER).id
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    api.post(f"/classes/{class_id}/archive", headers=headers)

    response = api.patch(
        f"/users/{prof_id}",
        json={
            "full_name": "User",
            "email": "prof@example.com",
            "role": UserRole.INSTRUCTOR.value,
            "class_id": str(class_id),
        },
        headers=headers,
    )

    assert response.status_code == 404


def test_class_archiving_is_manager_only(
    api: TestClient, seed_class: SeedClass, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = seed_class("Aleph")
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)

    by_teacher = auth_headers(api, "teacher")
    by_prof = auth_headers(api, "prof")

    assert api.post(f"/classes/{class_id}/archive", headers=by_teacher).status_code == 403
    assert api.post(f"/classes/{class_id}/restore", headers=by_prof).status_code == 403
    assert api.get("/classes/archived", headers=by_teacher).status_code == 403


def test_class_archiving_requires_authentication(api: TestClient) -> None:
    class_id = uuid.uuid4()
    assert api.post(f"/classes/{class_id}/archive").status_code == 401
    assert api.get("/classes/archived").status_code == 401


def test_refusal_message_reads_correctly_for_a_single_student(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    seed_student(class_id, "Dana")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/classes/{class_id}/archive", headers=headers)

    assert response.json()["message"] == (
        "לא ניתן להעביר את הכיתה לארכיון. משויכים אליה כעת — תלמידים פעילים: 1, משתמשים: 0."
    )


def test_disabled_user_does_not_block_archiving(
    api: TestClient,
    seed_class: SeedClass,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Bet")
    teacher_id = seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id).id
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    assert api.post(f"/classes/{class_id}/archive", headers=headers).status_code == 409

    api.post(f"/users/{teacher_id}/disable", headers=headers)

    assert api.post(f"/classes/{class_id}/archive", headers=headers).status_code == 200


def test_invited_user_still_blocks_archiving(
    api: TestClient,
    seed_class: SeedClass,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Bet")
    seed_user("pending", UserRole.INSTRUCTOR, class_id=class_id, status=UserStatus.INVITED)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/classes/{class_id}/archive", headers=headers)

    assert response.status_code == 409
