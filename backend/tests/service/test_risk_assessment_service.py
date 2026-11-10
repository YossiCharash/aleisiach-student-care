import uuid
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.risk_assessment_repository import RiskAssessmentRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_responsible_user_error import (
    InvalidResponsibleUserError,
)
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
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


def _request(
    assessment_date: date = date(2026, 9, 1),
    responsible: list[uuid.UUID] | None = None,
    nature: str = "אוכל מהר",
) -> RiskAssessmentRequest:
    return RiskAssessmentRequest(
        assessment_date=assessment_date,
        items=[
            RiskItemFields(
                domain=RiskDomain.EATING_DRINKING_SWALLOWING,
                nature=nature,
                level=RiskLevel.MEDIUM,
                intervention_plan="השגחה",
                responsible_user_ids=responsible or [],
            )
        ],
    )


def _setup(session: Session) -> tuple[RiskAssessmentService, uuid.UUID, uuid.UUID, uuid.UUID]:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    session.flush()
    service = RiskAssessmentService(
        RiskAssessmentRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )
    return service, student.id, workshop.id, seed_actor(session)


def test_create_fills_every_catalog_domain_in_order(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)

    created = service.create(student_id, _request(responsible=[actor]), _ALL, actor)

    assert [item.domain for item in created.items] == list(RiskDomain)
    first = created.items[0]
    assert first.level == RiskLevel.MEDIUM
    assert first.nature == "אוכל מהר"
    assert [member.full_name for member in first.responsible] == ["Actor"]
    assert created.items[1].level is None
    assert created.author_name == "Actor"


def test_history_carries_catalog_grouped_by_category(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    service.create(student_id, _request(), _ALL, actor)

    history = service.history(student_id, _ALL)

    assert history.student_name == "Dana"
    assert len(history.entries) == 1
    categories = [domain.category for domain in history.domains]
    assert categories[0] == RiskCategory.MEDICAL
    assert categories[-1] == RiskCategory.INDEPENDENCE
    assert history.domains[0].category_label == "רפואי"


def test_history_is_newest_first(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    service.create(student_id, _request(date(2026, 1, 1)), _ALL, actor)
    service.create(student_id, _request(date(2026, 6, 1)), _ALL, actor)

    dates = [entry.assessment_date for entry in service.history(student_id, _ALL).entries]

    assert dates == [date(2026, 6, 1), date(2026, 1, 1)]


def test_update_audits_changed_domains_only(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)

    updated = service.update(student_id, created.id, _request(nature="חנק"), _ALL, actor)

    assert updated.items[0].nature == "חנק"
    log = db_session.scalars(select(AuditLog).where(AuditLog.action == AuditAction.UPDATE)).one()
    assert log.changes == ["items.eating_drinking_swallowing"]


def test_unknown_responsible_user_is_rejected(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)

    with pytest.raises(InvalidResponsibleUserError):
        service.create(student_id, _request(responsible=[uuid.uuid4()]), _ALL, actor)


def test_candidates_exclude_disabled_users(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    disabled_id = seed_actor(db_session, "gone")
    disabled = db_session.get(User, disabled_id)
    assert disabled is not None
    disabled.status = UserStatus.DISABLED
    db_session.flush()

    candidates = service.responsible_candidates(student_id, _ALL)

    assert [member.id for member in candidates] == [actor]


def test_archive_hides_assessment_and_audits(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    created = service.create(student_id, _request(), _ALL, actor)

    service.archive(student_id, created.id, _ALL, actor)

    assert service.history(student_id, _ALL).entries == []
    actions = db_session.scalars(
        select(AuditLog.action).where(AuditLog.entity_type == "risk_assessment")
    ).all()
    assert list(actions) == [AuditAction.CREATE, AuditAction.ARCHIVE]


def test_entry_of_another_student_is_not_found(db_session: Session) -> None:
    service, student_id, workshop_id, actor = _setup(db_session)
    other = Student(full_name="Other", workshop_id=workshop_id)
    db_session.add(other)
    db_session.flush()
    created = service.create(student_id, _request(), _ALL, actor)

    with pytest.raises(NotFoundError):
        service.entry_history(other.id, created.id, _ALL)


def test_instructor_scope_outside_workshop_is_not_found(db_session: Session) -> None:
    service, student_id, _, actor = _setup(db_session)
    foreign_scope = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        service.create(student_id, _request(), foreign_scope, actor)


def test_request_rejects_duplicate_domains() -> None:
    item = RiskItemFields(domain=RiskDomain.WEIGHT)

    with pytest.raises(ValidationError):
        RiskAssessmentRequest(assessment_date=date(2026, 9, 1), items=[item, item])
