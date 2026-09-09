import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.label import Label
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
    def __init__(
        self, student_id: uuid.UUID, skill_area: uuid.UUID, solution_area: uuid.UUID
    ) -> None:
        self.student_id = student_id
        self.skill_area = skill_area
        self.solution_area = solution_area


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
    skill = Skill(sub_label_id=sub_label.id, name="הקשבה")
    session.add(skill)
    session.flush()
    solution = Solution(skill_id=skill.id, text="ישיבה בקדמת הקבוצה")
    session.add(solution)
    session.flush()
    return _Domain(student.id, skill.id, solution.id)


def _seed_area_foci(api: TestClient, domain: _Domain, headers: dict[str, str]) -> None:
    response = api.put(
        f"/students/{domain.student_id}/program",
        headers=headers,
        json={"entries": [{"skill_id": str(domain.skill_area), "rating": "yellow"}]},
    )
    assert response.status_code == 200


def _plan_body(domain: _Domain) -> dict[str, object]:
    return {
        "entries": [
            {"skill_id": str(domain.skill_area), "solution_ids": [str(domain.solution_area)]}
        ]
    }


def test_manager_creates_plan_and_list_reflects_it(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    _seed_area_foci(api, domain, headers)

    created = api.post(
        f"/students/{domain.student_id}/program/plans", headers=headers, json=_plan_body(domain)
    )
    assert created.status_code == 201
    entries = created.json()["entries"]
    assert entries[0]["skill_id"] == str(domain.skill_area)
    assert entries[0]["solutions"][0]["solution_id"] == str(domain.solution_area)

    listing = api.get(f"/students/{domain.student_id}/program/plans", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_new_plan_pushes_previous_to_history(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    _seed_area_foci(api, domain, headers)

    api.post(
        f"/students/{domain.student_id}/program/plans", headers=headers, json=_plan_body(domain)
    )
    api.post(
        f"/students/{domain.student_id}/program/plans", headers=headers, json=_plan_body(domain)
    )

    listing = api.get(f"/students/{domain.student_id}/program/plans", headers=headers)
    assert len(listing.json()) == 2


def test_plan_without_foci_is_rejected(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(
        f"/students/{domain.student_id}/program/plans", headers=headers, json=_plan_body(domain)
    )
    assert response.status_code == 422


def test_instructor_cannot_create_plan(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    _seed_area_foci(api, domain, auth_headers(api, "boss"))

    response = api.post(
        f"/students/{domain.student_id}/program/plans",
        headers=auth_headers(api, "teacher"),
        json=_plan_body(domain),
    )
    assert response.status_code == 403


def test_professional_teacher_can_read_plans(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    response = api.get(f"/students/{domain.student_id}/program/plans", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_plan_pdfs_are_served(
    api: TestClient, db_session: Session, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    _seed_area_foci(api, domain, headers)
    created = api.post(
        f"/students/{domain.student_id}/program/plans", headers=headers, json=_plan_body(domain)
    )
    plan_id = created.json()["id"]

    combined = api.get(f"/students/{domain.student_id}/program/plans/pdf", headers=headers)
    single = api.get(f"/students/{domain.student_id}/program/plans/{plan_id}/pdf", headers=headers)

    assert combined.status_code == 200
    assert combined.headers["content-type"] == "application/pdf"
    assert single.status_code == 200
    assert single.headers["content-type"] == "application/pdf"


def test_plans_require_authentication(api: TestClient, db_session: Session) -> None:
    workshop_id = _seed_workshop(db_session, "Aleph")
    domain = _seed_domain(db_session, workshop_id)

    response = api.get(f"/students/{domain.student_id}/program/plans")
    assert response.status_code == 401
