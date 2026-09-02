import uuid
from collections.abc import Callable

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label
from backend.app.models.client.student import Student
from backend.tests.conftest import DEFAULT_INSTITUTION_ID

SeedInstitution = Callable[..., Institution]


def _seed_class(session: Session, institution_id: uuid.UUID, name: str) -> ClassEntity:
    entity = ClassEntity(name=name, institution_id=institution_id)
    session.add(entity)
    session.flush()
    return entity


def _seed_student(session: Session, institution_id: uuid.UUID, name: str) -> Student:
    entity = _seed_class(session, institution_id, f"class-of-{name}")
    student = Student(full_name=name, class_id=entity.id, institution_id=institution_id)
    session.add(student)
    session.flush()
    return student


def test_select_returns_only_the_bound_institution(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    other = seed_institution("מוסד אחר", "other")
    _seed_student(db_session, DEFAULT_INSTITUTION_ID, "שלנו")
    _seed_student(db_session, other.id, "שלהם")

    names = [student.full_name for student in db_session.scalars(select(Student)).all()]

    assert names == ["שלנו"]


def test_each_binding_sees_its_own_rows(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    other = seed_institution("מוסד אחר", "other")
    _seed_student(db_session, DEFAULT_INSTITUTION_ID, "שלנו")
    _seed_student(db_session, other.id, "שלהם")

    TenantBinding.bind(db_session, other.id)
    theirs = [student.full_name for student in db_session.scalars(select(Student)).all()]
    TenantBinding.bind(db_session, DEFAULT_INSTITUTION_ID)
    ours = [student.full_name for student in db_session.scalars(select(Student)).all()]

    assert theirs == ["שלהם"]
    assert ours == ["שלנו"]


def test_get_by_id_hides_a_foreign_row(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    other = seed_institution("מוסד אחר", "other")
    foreign = _seed_student(db_session, other.id, "שלהם")

    assert StudentRepository(db_session).get(foreign.id) is None


def test_aggregate_counts_only_the_bound_institution(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    other = seed_institution("מוסד אחר", "other")
    _seed_student(db_session, DEFAULT_INSTITUTION_ID, "שלנו")
    _seed_student(db_session, other.id, "שלהם")

    assert db_session.scalar(select(func.count()).select_from(Student)) == 1


def test_new_rows_are_stamped_with_the_bound_institution(db_session: Session) -> None:
    entity = ClassEntity(name="ללא שיוך")
    db_session.add(entity)
    db_session.flush()

    assert entity.institution_id == DEFAULT_INSTITUTION_ID


def test_denied_binding_hides_every_row(db_session: Session) -> None:
    _seed_student(db_session, DEFAULT_INSTITUTION_ID, "שלנו")

    TenantBinding.deny(db_session)

    assert db_session.scalars(select(Student)).all() == []


def test_platform_scope_sees_every_institution(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    other = seed_institution("מוסד אחר", "other")
    _seed_class(db_session, DEFAULT_INSTITUTION_ID, "שלנו")
    _seed_class(db_session, other.id, "שלהם")

    with TenantBinding.platform(db_session):
        names = sorted(entity.name for entity in db_session.scalars(select(ClassEntity)).all())

    assert names == ["שלהם", "שלנו"]


def test_platform_scope_restores_the_previous_binding(db_session: Session) -> None:
    with TenantBinding.platform(db_session):
        assert TenantBinding.current(db_session) is None

    assert TenantBinding.current(db_session) == DEFAULT_INSTITUTION_ID


def test_require_rejects_a_denied_session(db_session: Session) -> None:
    TenantBinding.deny(db_session)

    with pytest.raises(AuthorizationError):
        TenantBinding.require(db_session)


def test_taxonomy_of_another_institution_is_hidden(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    other = seed_institution("מוסד אחר", "other")
    db_session.add(Label(name="שלהם", order=0, institution_id=other.id))
    db_session.add(Label(name="שלנו", order=0, institution_id=DEFAULT_INSTITUTION_ID))
    db_session.flush()

    names = [label.name for label in db_session.scalars(select(Label)).all()]

    assert names == ["שלנו"]
