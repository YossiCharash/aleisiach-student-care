from collections.abc import Callable

from sqlalchemy.orm import Session

from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.models.client.institution import Institution
from backend.tests.conftest import DEFAULT_INSTITUTION_ID

SeedInstitution = Callable[..., Institution]


def test_get_returns_the_stored_institution(db_session: Session) -> None:
    found = InstitutionRepository(db_session).get(DEFAULT_INSTITUTION_ID)

    assert found is not None
    assert found.name == "מוסד בדיקה"


def test_list_all_is_ordered_by_name_across_institutions(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    seed_institution("אלף")
    seed_institution("בית")

    names = [institution.name for institution in InstitutionRepository(db_session).list_all()]

    assert names == ["אלף", "בית", "מוסד בדיקה"]


def test_new_institutions_are_active(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    institution = seed_institution("מוסד חדש")

    assert institution.is_active is True
    assert institution.deactivated_at is None
