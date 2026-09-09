import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.workshop import Workshop

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


class _Domain:
    def __init__(self, student_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        self.student_id = student_id
        self.skill_id = skill_id


def _seed_workshop(session: Session, name: str) -> uuid.UUID:
    entity = Workshop(name=name)
    session.add(entity)
    session.flush()
    return entity.id


def _seed_domain(session: Session, workshop_id: uuid.UUID) -> _Domain:
    student = Student(full_name="Dana", workshop_id=workshop_id)
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
    solution = Solution(skill_id=skill.id, text="Daily", rating=MeetingRating.YELLOW)
    session.add(solution)
    session.flush()
    return _Domain(student.id, skill.id)


def _green_body(skill_id: uuid.UUID) -> dict[str, object]:
    return {"entries": [{"skill_id": str(skill_id), "rating": "green"}]}


def test_manager_creates_program_and_get_reflects_it(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.put(
        f"/students/{domain.student_id}/program", headers=headers, json=_green_body(domain.skill_id)
    )
    assert created.status_code == 200
    assert created.json()["exists"] is True

    program = api.get(f"/students/{domain.student_id}/program", headers=headers)
    assert program.status_code == 200
    strengths = program.json()["strengths"]
    assert [s["skill_id"] for s in strengths] == [str(domain.skill_id)]
    assert program.json()["areas_to_strengthen"] == []


def test_empty_program_is_rejected(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.put(
        f"/students/{domain.student_id}/program", headers=headers, json={"entries": []}
    )
    assert response.status_code == 422


def test_instructor_cannot_write_program(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    headers = auth_headers(api, "teacher")

    response = api.put(
        f"/students/{domain.student_id}/program", headers=headers, json=_green_body(domain.skill_id)
    )
    assert response.status_code == 403


def test_instructor_cannot_read_other_workshop_program(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    class_a = _seed_workshop(db_session, "Aleph")
    class_b = _seed_workshop(db_session, "Bet")
    domain = _seed_domain(db_session, class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=class_a)
    headers = auth_headers(api, "teacher")

    response = api.get(f"/students/{domain.student_id}/program", headers=headers)
    assert response.status_code == 404


def test_professional_teacher_can_read_program(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    response = api.get(f"/students/{domain.student_id}/program", headers=headers)

    assert response.status_code == 200
    assert response.json()["exists"] is False
    assert response.json()["strengths"] == []


def test_program_requires_authentication(api: TestClient, db_session: Session) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)

    response = api.get(f"/students/{domain.student_id}/program")
    assert response.status_code == 401
