import uuid
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.client.students.detail_option_repository import DetailOptionRepository
from backend.app.configuration.institutions.institution_template_settings import (
    InstitutionTemplateSettings,
)
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.detail_option_field import DetailOptionField
from backend.app.models.client.institution import Institution
from backend.app.models.client.risk_domain import RiskDomain
from backend.app.seed.institution_template_seeder import InstitutionTemplateSeeder
from backend.app.seed.risk_domain_seeder import RiskDomainSeeder

SeedInstitution = Callable[..., Institution]


def _seeder(session: Session, settings: InstitutionTemplateSettings) -> InstitutionTemplateSeeder:
    return InstitutionTemplateSeeder(
        DetailOptionRepository(session),
        RiskDomainSeeder(RiskDomainRepository(session), settings.risk_domains),
        settings,
    )


def _options(session: Session, institution_id: uuid.UUID) -> list[DetailOption]:
    with TenantBinding.platform(session):
        return list(
            session.scalars(
                select(DetailOption)
                .where(DetailOption.institution_id == institution_id)
                .order_by(DetailOption.field, DetailOption.order)
            ).all()
        )


def test_seeds_every_configured_field(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    institution = seed_institution("מוסד חדש")

    _seeder(db_session, InstitutionTemplateSettings()).seed(institution.id)

    fields = {option.field for option in _options(db_session, institution.id)}
    assert fields == set(DetailOptionField)


def test_seeded_options_keep_their_configured_order(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    institution = seed_institution("מוסד חדש")
    settings = InstitutionTemplateSettings(detail_options={"idd_severity": ("אחת", "שתיים")})

    _seeder(db_session, settings).seed(institution.id)

    seeded = _options(db_session, institution.id)
    assert [(option.name, option.order) for option in seeded] == [("אחת", 0), ("שתיים", 1)]


def test_seeded_options_belong_to_the_requested_institution_only(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    first = seed_institution("ראשון")
    second = seed_institution("שני")
    settings = InstitutionTemplateSettings(detail_options={"idd_severity": ("אחת",)})

    _seeder(db_session, settings).seed(first.id)

    assert len(_options(db_session, first.id)) == 1
    assert _options(db_session, second.id) == []


def test_an_empty_template_seeds_nothing(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    institution = seed_institution("מוסד חדש")

    _seeder(db_session, InstitutionTemplateSettings(detail_options={})).seed(institution.id)

    assert _options(db_session, institution.id) == []


def test_seeds_the_default_risk_domains(
    db_session: Session, seed_institution: SeedInstitution
) -> None:
    institution = seed_institution("מוסד חדש")

    _seeder(db_session, InstitutionTemplateSettings()).seed(institution.id)

    with TenantBinding.platform(db_session):
        names = db_session.scalars(
            select(RiskDomain.name).where(RiskDomain.institution_id == institution.id)
        ).all()
    assert len(names) == len(InstitutionTemplateSettings().risk_domains)
    assert "השארות בדירה באופן עצמאי" in names
