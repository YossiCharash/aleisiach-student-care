from collections.abc import Callable

from sqlalchemy.orm import Session

from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.models.client.institution import Institution
from backend.tests.conftest import DEFAULT_INSTITUTION_ID

SeedInstitution = Callable[..., Institution]


def test_get_returns_the_stored_institution(db_session: Session) -> None:
    found = InstitutionRepository(db_session).get(DEFAULT_INSTITUTION_ID)

    assert found is not None
    assert found.code == "test"


def test_get_by_code_finds_an_institution(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    seed_institution("מוסד נוסף", "second")

    found = InstitutionRepository(db_session).get_by_code("second")

    assert found is not None
    assert found.name == "מוסד נוסף"


def test_get_by_code_returns_none_when_unknown(db_session: Session) -> None:
    assert InstitutionRepository(db_session).get_by_code("missing") is None


def test_list_all_is_ordered_by_name_across_institutions(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    seed_institution("אלף", "alef")
    seed_institution("בית", "bet")

    names = [institution.name for institution in InstitutionRepository(db_session).list_all()]

    assert names == ["אלף", "בית", "מוסד בדיקה"]


def test_new_institutions_are_active(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    institution = seed_institution("מוסד חדש", "fresh")

    assert institution.is_active is True
    assert institution.deactivated_at is None
