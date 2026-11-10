import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.reports.health_domain_repository import HealthDomainRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.schema.routes.health_domain_create_request import HealthDomainCreateRequest
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.reports.health_domain_service import HealthDomainService
from backend.tests.support.seeding import seed_actor


def _service(session: Session) -> HealthDomainService:
    return HealthDomainService(
        HealthDomainRepository(session), AuditLogger(AuditLogRepository(session))
    )


def test_new_domains_are_appended_in_order(db_session: Session) -> None:
    service = _service(db_session)
    actor = seed_actor(db_session)

    first = service.create(HealthDomainCreateRequest(name="פיזיותרפיה"), actor)
    second = service.create(HealthDomainCreateRequest(name="ריפוי בעיסוק"), actor)

    assert (first.order, second.order) == (0, 1)
    assert [domain.name for domain in service.list_domains(False)] == [
        "פיזיותרפיה",
        "ריפוי בעיסוק",
    ]


def test_deactivated_domain_is_hidden_unless_requested(db_session: Session) -> None:
    service = _service(db_session)
    actor = seed_actor(db_session)
    domain = service.create(HealthDomainCreateRequest(name="פיזיותרפיה"), actor)

    renamed = service.update(
        domain.id, OrderedNodeUpdateRequest(name="פיזיו", is_active=False), actor
    )

    assert renamed.name == "פיזיו"
    assert service.list_domains(False) == []
    assert [item.id for item in service.list_domains(True)] == [domain.id]


def test_unknown_domain_is_not_found(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        _service(db_session).update(
            uuid.uuid4(), OrderedNodeUpdateRequest(name="x"), seed_actor(db_session)
        )
