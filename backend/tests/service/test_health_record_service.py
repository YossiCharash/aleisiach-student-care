import uuid
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.health_domain_repository import HealthDomainRepository
from backend.app.client.reports.health_record_repository import HealthRecordRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_health_domain_error import InvalidHealthDomainError
from backend.app.errors.service.invalid_responsible_user_error import (
    InvalidResponsibleUserError,
)
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.health_domain import HealthDomain
from backend.app.models.client.health_session_type import HealthSessionType
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.health_record_request import HealthRecordRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.health_record_service import HealthRecordService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock
from backend.tests.support.seeding import seed_actor, seed_health_domains, seed_student

_ALL = StudentAccessScope(all_workshops=True)


class _Setup:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.student_id = seed_student(session)
        self.domains: list[HealthDomain] = seed_health_domains(session)
        self.actor = seed_actor(session)
        self.service = HealthRecordService(
            HealthRecordRepository(session),
            HealthDomainRepository(session),
            UserRepository(session),
            StudentAccessGuard(StudentRepository(session)),
            AuditLogger(AuditLogRepository(session)),
            Clock(),
        )

    def request(
        self,
        record_date: date = date(2026, 9, 1),
        responsible: list[uuid.UUID] | None = None,
        support: str = "תרגול",
        domain: HealthDomain | None = None,
    ) -> HealthRecordRequest:
        return HealthRecordRequest(
            domain_id=(domain or self.domains[0]).id,
            record_date=record_date,
            session_type=HealthSessionType.GROUP,
            support_given=support,
            responsible_user_ids=responsible or [],
        )

    def audit_actions(self) -> list[tuple[AuditAction, list[str]]]:
        rows = self.session.scalars(
            select(AuditLog).where(AuditLog.entity_type == "health_record")
        ).all()
        return [(row.action, list(row.changes or [])) for row in rows]


def test_history_lists_rows_oldest_first(db_session: Session) -> None:
    setup = _Setup(db_session)
    late = setup.service.create(
        setup.student_id, setup.request(date(2026, 9, 5)), _ALL, setup.actor
    )
    early = setup.service.create(
        setup.student_id, setup.request(date(2026, 9, 1)), _ALL, setup.actor
    )

    history = setup.service.history(setup.student_id, _ALL)

    assert [entry.id for entry in history.entries] == [early.id, late.id]
    assert history.entries[0].author_name == "Actor"


def test_history_filtered_by_domain(db_session: Session) -> None:
    setup = _Setup(db_session)
    setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)
    other = setup.service.create(
        setup.student_id, setup.request(domain=setup.domains[1]), _ALL, setup.actor
    )

    history = setup.service.history(setup.student_id, _ALL, setup.domains[1].id)

    assert [entry.id for entry in history.entries] == [other.id]
    assert [domain.id for domain in history.domains] == [setup.domains[1].id]


def test_inactive_domain_rejected_for_new_rows_but_kept_on_edit(db_session: Session) -> None:
    setup = _Setup(db_session)
    entry = setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)
    setup.domains[0].is_active = False
    db_session.flush()

    with pytest.raises(InvalidHealthDomainError):
        setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)
    updated = setup.service.update(
        setup.student_id, entry.id, setup.request(support="עדכון"), _ALL, setup.actor
    )

    assert updated.support_given == "עדכון"
    history = setup.service.history(setup.student_id, _ALL)
    assert setup.domains[0].id in [domain.id for domain in history.domains]


def test_disabled_user_cannot_be_newly_assigned(db_session: Session) -> None:
    setup = _Setup(db_session)
    other = seed_actor(db_session, "other")
    user = db_session.get(User, other)
    assert user is not None
    user.status = UserStatus.DISABLED
    db_session.flush()

    with pytest.raises(InvalidResponsibleUserError):
        setup.service.create(
            setup.student_id, setup.request(responsible=[other]), _ALL, setup.actor
        )


def test_update_audits_only_changed_fields(db_session: Session) -> None:
    setup = _Setup(db_session)
    entry = setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)

    setup.service.update(setup.student_id, entry.id, setup.request(), _ALL, setup.actor)
    setup.service.update(
        setup.student_id, entry.id, setup.request(support="חדש"), _ALL, setup.actor
    )

    actions = setup.audit_actions()
    assert [action for action, _ in actions] == [AuditAction.CREATE, AuditAction.UPDATE]
    assert actions[1][1] == ["support_given"]


def test_archived_row_is_hidden_and_not_found(db_session: Session) -> None:
    setup = _Setup(db_session)
    entry = setup.service.create(setup.student_id, setup.request(), _ALL, setup.actor)

    setup.service.archive(setup.student_id, entry.id, _ALL, setup.actor)

    assert setup.service.history(setup.student_id, _ALL).entries == []
    with pytest.raises(NotFoundError):
        setup.service.archive(setup.student_id, entry.id, _ALL, setup.actor)


def test_empty_row_is_rejected_by_the_request() -> None:
    with pytest.raises(ValidationError):
        HealthRecordRequest(domain_id=uuid.uuid4(), record_date=date(2026, 9, 1), notes="  ")
