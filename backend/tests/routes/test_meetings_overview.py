import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def _seed_class(session: Session, name: str) -> uuid.UUID:
    entity = ClassEntity(name=name)
    session.add(entity)
    session.flush()
    return entity.id


def _seed_student(
    session: Session, name: str, class_id: uuid.UUID, is_archived: bool = False
) -> uuid.UUID:
    student = Student(full_name=name, class_id=class_id, is_archived=is_archived)
    session.add(student)
    session.flush()
    return student.id


def _seed_meeting(
    session: Session, student_id: uuid.UUID, author_id: uuid.UUID, year: int, month: int
) -> uuid.UUID:
    meeting = TeamMeeting(student_id=student_id, year=year, month=month, author_id=author_id)
    session.add(meeting)
    session.flush()
    return meeting.id


def test_manager_sees_overview_across_classes_newest_first(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    boss = seed_user("boss", UserRole.MANAGER)
    noa = _seed_student(db_session, "Noa", class_a)
    itai = _seed_student(db_session, "Itai", class_b)
    _seed_meeting(db_session, noa, boss.id, 2026, 9)
    _seed_meeting(db_session, itai, boss.id, 2026, 8)
    headers = auth_headers(api, "boss")

    response = api.get("/meetings/overview", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert [item["student_name"] for item in data] == ["Noa", "Itai"]
    assert data[0]["year"] == 2026
    assert data[0]["month"] == 9
    assert data[0]["student_id"] == str(noa)
    assert uuid.UUID(data[0]["meeting_id"])


def test_instructor_sees_only_own_class(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    boss = seed_user("boss", UserRole.MANAGER)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    mine = _seed_student(db_session, "Mine", class_a)
    other = _seed_student(db_session, "Other", class_b)
    _seed_meeting(db_session, mine, boss.id, 2026, 9)
    _seed_meeting(db_session, other, boss.id, 2026, 9)
    headers = auth_headers(api, "teacher")

    response = api.get("/meetings/overview", headers=headers)

    assert response.status_code == 200
    assert [item["student_name"] for item in response.json()] == ["Mine"]


def test_professional_teacher_sees_all_classes(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    boss = seed_user("boss", UserRole.MANAGER)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    student = _seed_student(db_session, "Dana", class_a)
    _seed_meeting(db_session, student, boss.id, 2026, 9)
    headers = auth_headers(api, "prof")

    response = api.get("/meetings/overview", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_overview_excludes_archived_students(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    boss = seed_user("boss", UserRole.MANAGER)
    active = _seed_student(db_session, "Active", class_a)
    archived = _seed_student(db_session, "Archived", class_a, is_archived=True)
    _seed_meeting(db_session, active, boss.id, 2026, 9)
    _seed_meeting(db_session, archived, boss.id, 2026, 9)
    headers = auth_headers(api, "boss")

    response = api.get("/meetings/overview", headers=headers)

    assert response.status_code == 200
    assert [item["student_name"] for item in response.json()] == ["Active"]
