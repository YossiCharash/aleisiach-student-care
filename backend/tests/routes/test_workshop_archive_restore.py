import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def test_manager_archives_and_restores_an_empty_workshop(
    api: TestClient, seed_workshop: SeedWorkshop, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = seed_workshop("Bet")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    archived = api.post(f"/workshops/{workshop_id}/archive", headers=headers)
    assert archived.status_code == 200

    assert api.get("/workshops", headers=headers).json() == []
    assert [row["id"] for row in api.get("/workshops/archived", headers=headers).json()] == [
        str(workshop_id)
    ]

    restored = api.post(f"/workshops/{workshop_id}/restore", headers=headers)
    assert restored.status_code == 200
    assert [row["id"] for row in api.get("/workshops", headers=headers).json()] == [
        str(workshop_id)
    ]


def test_archiving_a_workshop_with_students_returns_409(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    seed_student(workshop_id, "Dana")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/workshops/{workshop_id}/archive", headers=headers)

    assert response.status_code == 409
    assert response.json()["code"] == "workshop_not_empty"


def test_archived_workshop_cannot_receive_a_new_student(
    api: TestClient, seed_workshop: SeedWorkshop, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = seed_workshop("Bet")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    api.post(f"/workshops/{workshop_id}/archive", headers=headers)

    response = api.post(
        "/students",
        json={"full_name": "Newcomer", "workshop_id": str(workshop_id)},
        headers=headers,
    )

    assert response.status_code == 404


def test_workshop_archiving_is_manager_only(
    api: TestClient, seed_workshop: SeedWorkshop, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = seed_workshop("Aleph")
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)

    by_teacher = auth_headers(api, "teacher")
    by_prof = auth_headers(api, "prof")

    assert api.post(f"/workshops/{workshop_id}/archive", headers=by_teacher).status_code == 403
    assert api.post(f"/workshops/{workshop_id}/restore", headers=by_prof).status_code == 403
    assert api.get("/workshops/archived", headers=by_teacher).status_code == 403


def test_workshop_archiving_requires_authentication(api: TestClient) -> None:
    workshop_id = uuid.uuid4()
    assert api.post(f"/workshops/{workshop_id}/archive").status_code == 401
    assert api.get("/workshops/archived").status_code == 401


def test_refusal_message_reads_correctly_for_a_single_student(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    seed_student(workshop_id, "Dana")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/workshops/{workshop_id}/archive", headers=headers)

    assert response.json()["message"] == (
        "לא ניתן להעביר את הסדנה לארכיון. משויכים אליה כעת — חניכים פעילים: 1, משתמשים: 0."
    )


def test_disabled_user_does_not_block_archiving(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Bet")
    teacher_id = seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id).id
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    assert api.post(f"/workshops/{workshop_id}/archive", headers=headers).status_code == 409

    api.post(f"/users/{teacher_id}/disable", headers=headers)

    assert api.post(f"/workshops/{workshop_id}/archive", headers=headers).status_code == 200


def test_invited_user_still_blocks_archiving(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Bet")
    seed_user("pending", UserRole.INSTRUCTOR, workshop_id=workshop_id, status=UserStatus.INVITED)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/workshops/{workshop_id}/archive", headers=headers)

    assert response.status_code == 409
