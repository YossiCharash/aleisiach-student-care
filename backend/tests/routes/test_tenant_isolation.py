import uuid
from collections.abc import Callable
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.diagnosis_catalog import DiagnosisCatalog
from backend.app.models.client.extra_section_type import ExtraSectionType
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label
from backend.app.models.client.student import Student
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
    diagnosis_id: uuid.UUID
    section_type_id: uuid.UUID


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
    foreign_class, label, diagnosis, section_type, _ = entities
    student = Student(full_name="תלמיד זר", class_id=foreign_class.id, institution_id=owner)
    db_session.add(student)
    db_session.flush()
    return ForeignData(
        class_id=foreign_class.id,
        student_id=student.id,
        label_id=label.id,
        diagnosis_id=diagnosis.id,
        section_type_id=section_type.id,
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
