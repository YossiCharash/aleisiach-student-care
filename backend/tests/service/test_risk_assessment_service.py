import uuid
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.risk_assessment_repository import RiskAssessmentRepository
from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_responsible_user_error import (
    InvalidResponsibleUserError,
)
from backend.app.errors.service.invalid_risk_domain_error import InvalidRiskDomainError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain
from backend.app.models.client.risk_level import RiskLevel
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.risk_assessment_request import RiskAssessmentRequest
from backend.app.schema.routes.risk_item_fields import RiskItemFields
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.risk_assessment_service import RiskAssessmentService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.users.responsible_user_resolver import ResponsibleUserResolver
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor, seed_risk_domains

_ALL = StudentAccessScope(all_workshops=True)


class _Setup:
    def __init__(self, session: Session) -> None:
        workshop = Workshop(name="Aleph")
        session.add(workshop)
        session.flush()
        student = Student(full_name="Dana", workshop_id=workshop.id)
        session.add(student)
        session.flush()
        self.domains: list[RiskDomain] = seed_risk_domains(session)
        self.service = RiskAssessmentService(
            RiskAssessmentRepository(session),
            RiskDomainRepository(session),
            ResponsibleUserResolver(UserRepository(session)),
            StudentAccessGuard(StudentRepository(session)),
            AuditLogger(AuditLogRepository(session)),
            Clock(),
        )
        self.student_id = student.id
        self.workshop_id = workshop.id
        self.actor = seed_actor(session)

    def request(
        self,
        assessment_date: date = date(2026, 9, 1),
        responsible: list[uuid.UUID] | None = None,
        nature: str = "אוכל מהר",
        domain: RiskDomain | None = None,
    ) -> RiskAssessmentRequest:
        return RiskAssessmentRequest(
            assessment_date=assessment_date,
            items=[
                RiskItemFields(
                    domain_id=(domain or self.domains[0]).id,
                    nature=nature,
                    level=RiskLevel.MEDIUM,
                    intervention_plan="השגחה",
                    responsible_user_ids=responsible or [],
                )
            ],
        )


def test_create_stores_only_filled_rows_in_catalog_order(db_session: Session) -> None:
    setup = _Setup(db_session)
    first, second, third = setup.domains[0], setup.domains[1], setup.domains[2]
    request = RiskAssessmentRequest(
        assessment_date=date(2026, 9, 1),
        items=[
            RiskItemFields(domain_id=third.id, nature="ג"),
            RiskItemFields(domain_id=second.id),
            RiskItemFields(
                domain_id=first.id, level=RiskLevel.MEDIUM, responsible_user_ids=[setup.actor]
            ),
        ],
    )

    created = setup.service.create(setup.student_id, request, _ALL, setup.actor)

    assert [item.domain_id for item in created.items] == [first.id, third.id]
    assert [member.full_name for member in created.items[0].responsible] == ["Actor"]
    assert created.author_name == "Actor"


def test_history_lists_active_domains_grouped_by_category(db_session: Session) -> None:
    setup = _Setup(db_session)
    setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)

    history = setup.service.history(setup.student_id, _ALL)

    categories = [domain.category for domain in history.domains]
    assert categories[0] == RiskCategory.MEDICAL
    assert categories[-1] == RiskCategory.INDEPENDENCE
    assert history.domains[0].category_label == "רפואי"
    assert len(history.entries) == 1


def test_inactive_domain_is_hidden_unless_an_entry_uses_it(db_session: Session) -> None:
    setup = _Setup(db_session)
    used, unused = setup.domains[0], setup.domains[1]
    setup.service.create(setup.student_id, setup.request(domain=used), _ALL, setup.actor)
    used.is_active = False
    unused.is_active = False
    db_session.flush()

    ids = [domain.id for domain in setup.service.history(setup.student_id, _ALL).domains]

    assert used.id in ids
    assert unused.id not in ids


def test_new_table_rejects_inactive_domain_but_edit_keeps_it(db_session: Session) -> None:
    setup = _Setup(db_session)
    domain = setup.domains[0]
    created = setup.service.create(
        setup.student_id, setup.request(domain=domain), _ALL, setup.actor
    )
    domain.is_active = False
    db_session.flush()

    with pytest.raises(InvalidRiskDomainError):
        setup.service.create(setup.student_id, setup.request(domain=domain), _ALL, setup.actor)
    updated = setup.service.update(
        setup.student_id, created.id, setup.request(domain=domain, nature="חנק"), _ALL, setup.actor
    )

    assert updated.items[0].domain_id == domain.id
    assert updated.items[0].nature == "חנק"


def test_unknown_domain_is_rejected(db_session: Session) -> None:
    setup = _Setup(db_session)
    request = RiskAssessmentRequest(
        assessment_date=date(2026, 9, 1), items=[RiskItemFields(domain_id=uuid.uuid4())]
    )

    with pytest.raises(InvalidRiskDomainError):
        setup.service.create(setup.student_id, request, _ALL, setup.actor)


def test_history_is_newest_first(db_session: Session) -> None:
    setup = _Setup(db_session)
    setup.service.create(setup.student_id, setup.request(date(2026, 1, 1)), _ALL, setup.actor)
    setup.service.create(setup.student_id, setup.request(date(2026, 6, 1)), _ALL, setup.actor)

    entries = setup.service.history(setup.student_id, _ALL).entries

    assert [entry.assessment_date for entry in entries] == [date(2026, 6, 1), date(2026, 1, 1)]


def test_update_audits_changed_domains_only(db_session: Session) -> None:
    setup = _Setup(db_session)
    created = setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)

    setup.service.update(
        setup.student_id, created.id, setup.request(nature="חנק"), _ALL, setup.actor
    )

    log = db_session.scalars(select(AuditLog).where(AuditLog.action == AuditAction.UPDATE)).one()
    assert log.changes == [f"items.{setup.domains[0].id}"]


def test_unknown_responsible_user_is_rejected(db_session: Session) -> None:
    setup = _Setup(db_session)

    with pytest.raises(InvalidResponsibleUserError):
        setup.service.create(
            setup.student_id, setup.request(responsible=[uuid.uuid4()]), _ALL, setup.actor
        )


def test_disabled_user_cannot_be_newly_assigned_but_stays_if_already_assigned(
    db_session: Session,
) -> None:
    setup = _Setup(db_session)
    helper_id = seed_actor(db_session, "helper")
    created = setup.service.create(
        setup.student_id, setup.request(responsible=[helper_id]), _ALL, setup.actor
    )
    helper = db_session.get(User, helper_id)
    assert helper is not None
    helper.status = UserStatus.DISABLED
    db_session.flush()

    kept = setup.service.update(
        setup.student_id,
        created.id,
        setup.request(responsible=[helper_id], nature="x"),
        _ALL,
        setup.actor,
    )

    assert kept.items[0].responsible_user_ids == [helper_id]
    with pytest.raises(InvalidResponsibleUserError):
        setup.service.create(
            setup.student_id, setup.request(responsible=[helper_id]), _ALL, setup.actor
        )


def test_candidates_exclude_disabled_users(db_session: Session) -> None:
    setup = _Setup(db_session)
    disabled_id = seed_actor(db_session, "gone")
    disabled = db_session.get(User, disabled_id)
    assert disabled is not None
    disabled.status = UserStatus.DISABLED
    db_session.flush()

    candidates = setup.service.responsible_candidates(setup.student_id, _ALL)

    assert [member.id for member in candidates] == [setup.actor]


def test_archive_hides_assessment_and_audits(db_session: Session) -> None:
    setup = _Setup(db_session)
    created = setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)

    setup.service.archive(setup.student_id, created.id, _ALL, setup.actor)

    assert setup.service.history(setup.student_id, _ALL).entries == []
    actions = db_session.scalars(
        select(AuditLog.action).where(AuditLog.entity_type == "risk_assessment")
    ).all()
    assert list(actions) == [AuditAction.CREATE, AuditAction.ARCHIVE]


def test_entry_of_another_student_is_not_found(db_session: Session) -> None:
    setup = _Setup(db_session)
    other = Student(full_name="Other", workshop_id=setup.workshop_id)
    db_session.add(other)
    db_session.flush()
    created = setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)

    with pytest.raises(NotFoundError):
        setup.service.entry_history(other.id, created.id, _ALL)


def test_instructor_scope_outside_workshop_is_not_found(db_session: Session) -> None:
    setup = _Setup(db_session)
    foreign_scope = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        setup.service.create(setup.student_id, setup.request(), foreign_scope, setup.actor)


def test_request_rejects_duplicate_domains() -> None:
    item = RiskItemFields(domain_id=uuid.uuid4())

    with pytest.raises(ValidationError):
        RiskAssessmentRequest(assessment_date=date(2026, 9, 1), items=[item, item])
