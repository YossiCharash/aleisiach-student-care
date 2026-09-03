import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.schema.routes.label_create_request import LabelCreateRequest
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.schema.routes.skill_create_request import SkillCreateRequest
from backend.app.schema.routes.solution_create_request import SolutionCreateRequest
from backend.app.schema.routes.sub_label_create_request import SubLabelCreateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.taxonomy.taxonomy_service import TaxonomyService

_ACTOR = uuid.uuid4()


def _service(session: Session) -> TaxonomyService:
    return TaxonomyService(TaxonomyRepository(session), AuditLogger(AuditLogRepository(session)))


def test_create_label_assigns_incrementing_order(db_session: Session) -> None:
    service = _service(db_session)

    first = service.create_label(LabelCreateRequest(name="עצמאות"), _ACTOR)
    second = service.create_label(LabelCreateRequest(name="תקשורת"), _ACTOR)

    assert first.order == 0
    assert second.order == 1
    assert first.is_active is True


def test_create_sub_label_under_unknown_label_raises(db_session: Session) -> None:
    service = _service(db_session)

    try:
        service.create_sub_label(SubLabelCreateRequest(label_id=uuid.uuid4(), name="x"), _ACTOR)
        raise AssertionError("expected NotFoundError")
    except NotFoundError as error:
        assert error.resource == "label"


def test_active_tree_nests_children_and_hides_inactive(db_session: Session) -> None:
    service = _service(db_session)
    label = service.create_label(LabelCreateRequest(name="עצמאות"), _ACTOR)
    sub_label = service.create_sub_label(
        SubLabelCreateRequest(label_id=label.id, name="היגיינה"), _ACTOR
    )
    skill = service.create_skill(
        SkillCreateRequest(sub_label_id=sub_label.id, name="רחיצת ידיים"), _ACTOR
    )
    service.create_solution(SolutionCreateRequest(skill_id=skill.id, text="תרגול יומי"), _ACTOR)
    hidden = service.create_label(LabelCreateRequest(name="מוסתר"), _ACTOR)
    service.update_label(hidden.id, OrderedNodeUpdateRequest(is_active=False), _ACTOR)

    tree = service.active_tree()

    assert [node.name for node in tree] == ["עצמאות"]
    assert tree[0].sub_labels[0].skills[0].solutions[0].text == "תרגול יומי"


def test_deactivating_skill_removes_it_from_tree(db_session: Session) -> None:
    service = _service(db_session)
    label = service.create_label(LabelCreateRequest(name="עצמאות"), _ACTOR)
    sub_label = service.create_sub_label(
        SubLabelCreateRequest(label_id=label.id, name="היגיינה"), _ACTOR
    )
    skill = service.create_skill(
        SkillCreateRequest(sub_label_id=sub_label.id, name="רחיצת ידיים"), _ACTOR
    )

    service.update_skill(skill.id, OrderedNodeUpdateRequest(is_active=False), _ACTOR)

    tree = service.active_tree()
    assert tree[0].sub_labels[0].skills == []


def test_create_and_update_label_are_audited(db_session: Session) -> None:
    service = _service(db_session)

    label = service.create_label(LabelCreateRequest(name="עצמאות"), _ACTOR)
    service.update_label(label.id, OrderedNodeUpdateRequest(name="חדש"), _ACTOR)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert [log.action for log in logs] == [AuditAction.CREATE, AuditAction.UPDATE]
    assert all(log.entity_type == "taxonomy" for log in logs)
    assert all(log.actor_id == _ACTOR for log in logs)
    assert "name" in logs[-1].changes
