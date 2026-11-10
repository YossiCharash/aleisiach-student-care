import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.risk_category import RiskCategory
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.schema.routes.risk_domain_create_request import RiskDomainCreateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.risk_domain_service import RiskDomainService
from backend.tests.support.seeding import seed_actor


def _service(session: Session) -> RiskDomainService:
    return RiskDomainService(
        RiskDomainRepository(session), AuditLogger(AuditLogRepository(session))
    )


def test_new_domains_are_appended_within_their_category(db_session: Session) -> None:
    service = _service(db_session)
    actor = seed_actor(db_session)

    first = service.create(RiskDomainCreateRequest(name="א", category=RiskCategory.MEDICAL), actor)
    second = service.create(RiskDomainCreateRequest(name="ב", category=RiskCategory.MEDICAL), actor)
    other = service.create(
        RiskDomainCreateRequest(name="ג", category=RiskCategory.INDEPENDENCE), actor
    )

    assert (first.order, second.order, other.order) == (0, 1, 0)


def test_list_is_ordered_by_category_then_order(db_session: Session) -> None:
    service = _service(db_session)
    actor = seed_actor(db_session)
    service.create(
        RiskDomainCreateRequest(name="עצמאות", category=RiskCategory.INDEPENDENCE), actor
    )
    service.create(RiskDomainCreateRequest(name="רפואי", category=RiskCategory.MEDICAL), actor)

    names = [domain.name for domain in service.list_domains(include_inactive=False)]

    assert names == ["רפואי", "עצמאות"]


def test_deactivated_domain_is_listed_only_with_inactive(db_session: Session) -> None:
    service = _service(db_session)
    actor = seed_actor(db_session)
    domain = service.create(RiskDomainCreateRequest(name="א", category=RiskCategory.MEDICAL), actor)

    service.update(domain.id, OrderedNodeUpdateRequest(is_active=False), actor)

    assert service.list_domains(include_inactive=False) == []
    assert [item.id for item in service.list_domains(include_inactive=True)] == [domain.id]
    changes = db_session.scalars(select(AuditLog.changes)).all()
    assert ["is_active"] in changes


def test_update_of_unknown_domain_is_not_found(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        _service(db_session).update(
            uuid.uuid4(), OrderedNodeUpdateRequest(name="x"), seed_actor(db_session)
        )
