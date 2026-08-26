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
    def __init__(self, student_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        self.student_id = student_id
        self.skill_id = skill_id


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
    return _Domain(student.id, skill.id)


def test_program_reflects_latest_meeting(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    body = {
        "year": 2026,
        "month": 8,
        "entries": [{"skill_id": str(domain.skill_id), "rating": "green", "solution_ids": []}],
    }
    api.post(f"/students/{domain.student_id}/meetings", headers=headers, json=body)

    program = api.get(f"/students/{domain.student_id}/program", headers=headers)

    assert program.status_code == 200
    strengths = program.json()["strengths"]
    assert [s["skill_id"] for s in strengths] == [str(domain.skill_id)]
    assert program.json()["areas_to_strengthen"] == []


def test_instructor_cannot_read_other_class_program(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_class(db_session, "Aleph")
    class_b = _seed_class(db_session, "Bet")
    domain = _seed_domain(db_session, class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_a)
    headers = auth_headers(api, "teacher")

    response = api.get(f"/students/{domain.student_id}/program", headers=headers)
    assert response.status_code == 404


def test_professional_teacher_can_read_program(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    response = api.get(f"/students/{domain.student_id}/program", headers=headers)

    assert response.status_code == 200
    assert response.json()["strengths"] == []


def test_program_requires_authentication(api: TestClient, db_session: Session) -> None:
    class_id = _seed_class(db_session, "Aleph")
    domain = _seed_domain(db_session, class_id)

    response = api.get(f"/students/{domain.student_id}/program")
    assert response.status_code == 401
