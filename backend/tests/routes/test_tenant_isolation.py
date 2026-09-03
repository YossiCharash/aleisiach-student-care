import uuid
from collections.abc import Callable
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.detail_option_field import DetailOptionField
from backend.app.models.client.diagnosis_catalog import DiagnosisCatalog
from backend.app.models.client.extra_section_type import ExtraSectionType
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.utils.service.password_hasher import PasswordHasher

SeedUser = Callable[..., User]
SeedInstitution = Callable[..., Institution]
AuthHeaders = Callable[..., dict[str, str]]

FOREIGN_EMAIL = "foreign@example.com"


@dataclass(frozen=True)
class ForeignData:
    class_id: uuid.UUID
    student_id: uuid.UUID
    label_id: uuid.UUID
    sub_label_id: uuid.UUID
    skill_id: uuid.UUID
    solution_id: uuid.UUID
    diagnosis_id: uuid.UUID
    section_type_id: uuid.UUID
    option_id: uuid.UUID
    meeting_id: uuid.UUID
    user_id: uuid.UUID


@pytest.fixture
def foreign(db_session: Session, seed_institution: SeedInstitution) -> ForeignData:
    owner = seed_institution("מוסד זר", "foreign").id
    entities = [
        ClassEntity(name="כיתה זרה", institution_id=owner),
        Label(name="תווית זרה", order=0, institution_id=owner),
        DiagnosisCatalog(name="אבחון זר", order=0, institution_id=owner),
        ExtraSectionType(name="סעיף זר", order=0, institution_id=owner),
        User(
            full_name="מנהל זר",
            email=FOREIGN_EMAIL,
            username="foreign-manager",
            password_hash=PasswordHasher().hash("password123"),
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            institution_id=owner,
        ),
    ]
    db_session.add_all(entities)
    db_session.flush()
    foreign_class, label, diagnosis, section_type, manager = entities
    student = Student(full_name="תלמיד זר", class_id=foreign_class.id, institution_id=owner)
    sub_label = SubLabel(name="תת-תווית זרה", order=0, label_id=label.id, institution_id=owner)
    option = DetailOption(
        field=DetailOptionField.ASSISTIVE_DEVICE, name="אביזר זר", order=0, institution_id=owner
    )
    db_session.add_all([student, sub_label, option])
    db_session.flush()
    skill = Skill(name="מיומנות זרה", order=0, sub_label_id=sub_label.id, institution_id=owner)
    db_session.add(skill)
    db_session.flush()
    solution = Solution(text="פתרון זר", skill_id=skill.id, institution_id=owner)
    meeting = TeamMeeting(
        student_id=student.id,
        year=2026,
        month=5,
        author_id=manager.id,
        institution_id=owner,
    )
    meeting.entries = [
        MeetingEntry(
            skill_id=skill.id,
            skill_name_snapshot=skill.name,
            rating=MeetingRating.GREEN,
            position=0,
            institution_id=owner,
        )
    ]
    db_session.add_all([solution, meeting])
    db_session.flush()
    return ForeignData(
        class_id=foreign_class.id,
        student_id=student.id,
        label_id=label.id,
        sub_label_id=sub_label.id,
        skill_id=skill.id,
        solution_id=solution.id,
        diagnosis_id=diagnosis.id,
        section_type_id=section_type.id,
        option_id=option.id,
        meeting_id=meeting.id,
        user_id=manager.id,
    )


@pytest.fixture
def manager_headers(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> dict[str, str]:
    seed_user("boss", UserRole.MANAGER)
    return auth_headers(api, "boss")


def test_foreign_student_is_not_found(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.get(f"/students/{foreign.student_id}", headers=manager_headers)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "suffix", ["details", "social-note", "program", "extra-sections", "meetings"]
)
def test_foreign_student_sub_resources_are_not_found(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], suffix: str
) -> None:
    response = api.get(f"/students/{foreign.student_id}/{suffix}", headers=manager_headers)

    assert response.status_code == 404


def test_student_list_excludes_other_institutions(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.get("/students", headers=manager_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_class_list_excludes_other_institutions(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.get("/classes", headers=manager_headers)

    assert response.json() == []


def test_user_list_excludes_other_institutions(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.get("/users", headers=manager_headers)

    assert FOREIGN_EMAIL not in [item["email"] for item in response.json()]


@pytest.mark.parametrize(
    "path", ["/taxonomy/labels", "/diagnoses", "/extra-section-types", "/detail-options"]
)
def test_catalog_lists_exclude_other_institutions(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], path: str
) -> None:
    response = api.get(path, headers=manager_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_foreign_label_cannot_be_renamed(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.patch(
        f"/taxonomy/labels/{foreign.label_id}", headers=manager_headers, json={"name": "נחטף"}
    )

    assert response.status_code == 404


def test_foreign_diagnosis_cannot_be_renamed(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.patch(
        f"/diagnoses/{foreign.diagnosis_id}", headers=manager_headers, json={"name": "נחטף"}
    )

    assert response.status_code == 404


def test_foreign_section_type_cannot_be_renamed(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.patch(
        f"/extra-section-types/{foreign.section_type_id}",
        headers=manager_headers,
        json={"name": "נחטף"},
    )

    assert response.status_code == 404


def test_student_cannot_be_created_in_a_foreign_class(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.post(
        "/students",
        headers=manager_headers,
        json={"full_name": "חדש", "class_id": str(foreign.class_id)},
    )

    assert response.status_code == 404


def test_foreign_class_cannot_be_renamed(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.patch(
        f"/classes/{foreign.class_id}", headers=manager_headers, json={"name": "נחטף"}
    )

    assert response.status_code == 404


def test_manager_cannot_invite_a_super_admin(
    api: TestClient, manager_headers: dict[str, str]
) -> None:
    response = api.post(
        "/auth/invitations",
        headers=manager_headers,
        json={"full_name": "מנהל על", "email": "root@example.org", "role": "super_admin"},
    )

    assert response.status_code == 403


def test_manager_cannot_promote_a_user_to_super_admin(
    api: TestClient, manager_headers: dict[str, str], seed_user: SeedUser
) -> None:
    target = seed_user("dana", UserRole.INSTRUCTOR)

    response = api.patch(
        f"/users/{target.id}",
        headers=manager_headers,
        json={"full_name": "דנה", "email": "dana@example.com", "role": "super_admin"},
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("method", "suffix"),
    [
        ("patch", ""),
        ("post", "/archive"),
        ("post", "/restore"),
        ("put", "/details"),
        ("get", "/details/pdf"),
        ("post", "/meetings"),
        ("put", "/social-note"),
    ],
)
def test_foreign_student_write_paths_are_not_found(
    api: TestClient,
    foreign: ForeignData,
    manager_headers: dict[str, str],
    method: str,
    suffix: str,
) -> None:
    body = {
        "": {"full_name": "נחטף", "class_id": str(foreign.class_id)},
        "/details": {},
        "/social-note": {"content": "נחטף"},
        "/meetings": {
            "year": 2026,
            "month": 6,
            "entries": [{"skill_id": str(foreign.skill_id), "rating": "green"}],
        },
    }.get(suffix)
    call = getattr(api, method)
    path = f"/students/{foreign.student_id}{suffix}"

    response = (
        call(path, headers=manager_headers)
        if body is None
        else call(path, headers=manager_headers, json=body)
    )

    assert response.status_code == 404


@pytest.mark.parametrize("suffix", ["", "/pdf"])
def test_foreign_meeting_is_not_found(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], suffix: str
) -> None:
    path = f"/students/{foreign.student_id}/meetings/{foreign.meeting_id}{suffix}"

    assert api.get(path, headers=manager_headers).status_code == 404


def test_foreign_extra_section_cannot_be_written(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.put(
        f"/students/{foreign.student_id}/extra-sections/{foreign.section_type_id}",
        headers=manager_headers,
        json={"content": "נחטף"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("path", ["/students/archived", "/classes/archived"])
def test_archived_lists_exclude_other_institutions(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], path: str
) -> None:
    response = api.get(path, headers=manager_headers)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("action", ["archive", "restore"])
def test_foreign_class_cannot_be_archived_or_restored(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], action: str
) -> None:
    response = api.post(f"/classes/{foreign.class_id}/{action}", headers=manager_headers)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("collection", "attribute"),
    [
        ("sub-labels", "sub_label_id"),
        ("skills", "skill_id"),
        ("solutions", "solution_id"),
    ],
)
def test_foreign_taxonomy_nodes_cannot_be_updated(
    api: TestClient,
    foreign: ForeignData,
    manager_headers: dict[str, str],
    collection: str,
    attribute: str,
) -> None:
    node_id = getattr(foreign, attribute)
    body = {"text": "נחטף"} if collection == "solutions" else {"name": "נחטף"}

    response = api.patch(f"/taxonomy/{collection}/{node_id}", headers=manager_headers, json=body)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("collection", "body_key", "attribute"),
    [
        ("sub-labels", "label_id", "label_id"),
        ("skills", "sub_label_id", "sub_label_id"),
        ("solutions", "skill_id", "skill_id"),
    ],
)
def test_taxonomy_children_cannot_hang_off_a_foreign_parent(
    api: TestClient,
    foreign: ForeignData,
    manager_headers: dict[str, str],
    collection: str,
    body_key: str,
    attribute: str,
) -> None:
    payload: dict[str, str] = {body_key: str(getattr(foreign, attribute))}
    payload["text" if collection == "solutions" else "name"] = "נחטף"

    response = api.post(f"/taxonomy/{collection}", headers=manager_headers, json=payload)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("collection", "attribute"),
    [
        ("sub-labels?label_id=", "label_id"),
        ("skills?sub_label_id=", "sub_label_id"),
        ("solutions?skill_id=", "skill_id"),
    ],
)
def test_taxonomy_children_of_a_foreign_parent_are_not_found(
    api: TestClient,
    foreign: ForeignData,
    manager_headers: dict[str, str],
    collection: str,
    attribute: str,
) -> None:
    response = api.get(
        f"/taxonomy/{collection}{getattr(foreign, attribute)}", headers=manager_headers
    )

    assert response.status_code == 404


@pytest.mark.parametrize("path", ["/taxonomy/tree", "/extra-section-types/tree"])
def test_trees_exclude_other_institutions(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], path: str
) -> None:
    response = api.get(path, headers=manager_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_foreign_detail_option_cannot_be_updated(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.patch(
        f"/detail-options/{foreign.option_id}", headers=manager_headers, json={"name": "נחטף"}
    )

    assert response.status_code == 404


def test_foreign_user_cannot_be_edited(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.patch(
        f"/users/{foreign.user_id}",
        headers=manager_headers,
        json={"full_name": "נחטף", "email": FOREIGN_EMAIL, "role": "manager"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("action", ["disable", "enable"])
def test_foreign_user_cannot_be_disabled_or_enabled(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str], action: str
) -> None:
    response = api.post(f"/users/{foreign.user_id}/{action}", headers=manager_headers)

    assert response.status_code == 404


def test_section_type_cannot_hang_off_a_foreign_parent(
    api: TestClient, foreign: ForeignData, manager_headers: dict[str, str]
) -> None:
    response = api.post(
        "/extra-section-types",
        headers=manager_headers,
        json={"name": "נחטף", "parent_id": str(foreign.section_type_id)},
    )

    assert response.status_code == 404
