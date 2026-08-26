import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def _seed_class(session: Session, name: str) -> uuid.UUID:
    entity = ClassEntity(name=name)
    session.add(entity)
    session.flush()
    return entity.id


def _seed_student(session: Session, name: str, class_id: uuid.UUID) -> uuid.UUID:
    student = Student(full_name=name, class_id=class_id)
    session.add(student)
    session.flush()
    return student.id


def test_manager_creates_and_reads_student(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post(
        "/students", headers=headers, json={"full_name": "Dana", "class_id": str(class_id)}
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    fetched = api.get(f"/students/{student_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Dana"


def test_create_requires_authentication(api: TestClient, db_session: Session) -> None:
    class_id = _seed_class(db_session, "Aleph")
    response = api.post("/students", json={"full_name": "X", "class_id": str(class_id)})
    assert response.status_code == 401


def test_create_with_unknown_class_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(
        "/students", headers=headers, json={"full_name": "X", "class_id": str(uuid.uuid4())}
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_instructor_cannot_create_student(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)
    headers = auth_headers(api, "teacher")

    response = api.post(
        "/students", headers=headers, json={"full_name": "X", "class_id": str(class_id)}
    )
    assert response.status_code == 403


def test_instructor_lists_only_own_class(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    _seed_student(db_session, "Own", class_a)
    _seed_student(db_session, "Other", class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    headers = auth_headers(api, "teacher")

    names = [student["full_name"] for student in api.get("/students", headers=headers).json()]
    assert names == ["Own"]


def test_instructor_cannot_read_other_class_student(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    other_id = _seed_student(db_session, "Other", class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    headers = auth_headers(api, "teacher")

    response = api.get(f"/students/{other_id}", headers=headers)
    assert response.status_code == 404


def test_professional_teacher_reads_all_but_cannot_create(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    _seed_student(db_session, "One", class_a)
    _seed_student(db_session, "Two", class_b)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    names = [student["full_name"] for student in api.get("/students", headers=headers).json()]
    assert names == ["One", "Two"]

    forbidden = api.post(
        "/students", headers=headers, json={"full_name": "X", "class_id": str(class_a)}
    )
    assert forbidden.status_code == 403


def test_only_manager_archives_and_it_hides_student(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    student_id = _seed_student(db_session, "Goes", class_id)
    seed_user("boss", UserRole.MANAGER)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)

    instructor_headers = auth_headers(api, "teacher")
    assert (
        api.post(f"/students/{student_id}/archive", headers=instructor_headers).status_code == 403
    )

    manager_headers = auth_headers(api, "boss")
    archived = api.post(f"/students/{student_id}/archive", headers=manager_headers)
    assert archived.status_code == 200
    assert archived.json()["is_archived"] is True
    assert api.get("/students", headers=manager_headers).json() == []
