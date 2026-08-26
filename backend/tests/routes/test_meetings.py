import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.label import Label
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


class _Domain:
    def __init__(
        self,
        class_id: uuid.UUID,
        student_id: uuid.UUID,
        skill_id: uuid.UUID,
        solution_id: uuid.UUID,
    ) -> None:
        self.class_id = class_id
        self.student_id = student_id
        self.skill_id = skill_id
        self.solution_id = solution_id


def _seed_class(session: Session, name: str) -> uuid.UUID:
    entity = ClassEntity(name=name)
    session.add(entity)
    session.flush()
    return entity.id


def _seed_domain(session: Session, class_id: uuid.UUID) -> _Domain:
    student = Student(full_name="Dana", class_id=class_id)
    session.add(student)
    label = Label(name="L")
    session.add(label)
    session.flush()
    sub_label = SubLabel(label_id=label.id, name="S")
    session.add(sub_label)
    session.flush()
    skill = Skill(sub_label_id=sub_label.id, name="Wash")
    session.add(skill)
    session.flush()
    solution = Solution(skill_id=skill.id, text="Daily")
    session.add(solution)
    session.flush()
    return _Domain(class_id, student.id, skill.id, solution.id)


def _entry(skill_id: uuid.UUID, rating: str, solution_ids: list[str]) -> dict[str, object]:
    return {"skill_id": str(skill_id), "rating": rating, "solution_ids": solution_ids}


def test_instructor_creates_meeting_for_own_class(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)
    headers = auth_headers(api, "teacher")

    body = {
        "year": 2026,
        "month": 8,
        "entries": [_entry(domain.skill_id, "yellow", [str(domain.solution_id)])],
    }
    response = api.post(f"/students/{domain.student_id}/meetings", headers=headers, json=body)

    assert response.status_code == 201
    entry = response.json()["entries"][0]
    assert entry["skill_name_snapshot"] == "Wash"
    assert entry["solutions"][0]["solution_text_snapshot"] == "Daily"


def test_professional_teacher_cannot_write_but_can_read(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    body = {
        "year": 2026,
        "month": 8,
        "entries": [_entry(domain.skill_id, "green", [])],
    }
    write = api.post(f"/students/{domain.student_id}/meetings", headers=headers, json=body)
    assert write.status_code == 403

    read = api.get(f"/students/{domain.student_id}/meetings", headers=headers)
    assert read.status_code == 200
    assert read.json() == []


def test_instructor_cannot_write_for_other_class(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    domain = _seed_domain(db_session, class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    headers = auth_headers(api, "teacher")

    body = {
        "year": 2026,
        "month": 8,
        "entries": [_entry(domain.skill_id, "green", [])],
    }
    response = api.post(f"/students/{domain.student_id}/meetings", headers=headers, json=body)
    assert response.status_code == 404


def test_yellow_without_solution_returns_422(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    body = {
        "year": 2026,
        "month": 8,
        "entries": [_entry(domain.skill_id, "red", [])],
    }
    response = api.post(f"/students/{domain.student_id}/meetings", headers=headers, json=body)
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_meeting"


def test_get_meeting_validates_it_belongs_to_the_url_student(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)
    other_student = Student(full_name="Roni", class_id=class_id)
    db_session.add(other_student)
    db_session.flush()
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    body = {"year": 2026, "month": 8, "entries": [_entry(domain.skill_id, "green", [])]}
    meeting_id = api.post(
        f"/students/{domain.student_id}/meetings", headers=headers, json=body
    ).json()["id"]

    correct = api.get(f"/students/{domain.student_id}/meetings/{meeting_id}", headers=headers)
    assert correct.status_code == 200

    mismatched = api.get(f"/students/{other_student.id}/meetings/{meeting_id}", headers=headers)
    assert mismatched.status_code == 404


def test_writing_requires_authentication(api: TestClient, db_session: Session) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)

    body = {"year": 2026, "month": 8, "entries": [_entry(domain.skill_id, "green", [])]}
    response = api.post(f"/students/{domain.student_id}/meetings", json=body)
    assert response.status_code == 401
