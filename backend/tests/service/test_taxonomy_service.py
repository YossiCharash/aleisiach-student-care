import uuid

from sqlalchemy.orm import Session

from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.schema.routes.label_create_request import LabelCreateRequest
from backend.app.schema.routes.label_update_request import LabelUpdateRequest
from backend.app.schema.routes.skill_create_request import SkillCreateRequest
from backend.app.schema.routes.skill_update_request import SkillUpdateRequest
from backend.app.schema.routes.solution_create_request import SolutionCreateRequest
from backend.app.schema.routes.sub_label_create_request import SubLabelCreateRequest
from backend.app.service.taxonomy.taxonomy_service import TaxonomyService


def _service(session: Session) -> TaxonomyService:
    return TaxonomyService(TaxonomyRepository(session))


def test_create_label_assigns_incrementing_order(db_session: Session) -> None:
    service = _service(db_session)

    first = service.create_label(LabelCreateRequest(name="עצמאות"))
    second = service.create_label(LabelCreateRequest(name="תקשורת"))

    assert first.order == 0
    assert second.order == 1
    assert first.is_active is True


def test_create_sub_label_under_unknown_label_raises(db_session: Session) -> None:
    service = _service(db_session)

    try:
        service.create_sub_label(SubLabelCreateRequest(label_id=uuid.uuid4(), name="x"))
        raise AssertionError("expected NotFoundError")
    except NotFoundError as error:
        assert error.resource == "label"


def test_active_tree_nests_children_and_hides_inactive(db_session: Session) -> None:
    service = _service(db_session)
    label = service.create_label(LabelCreateRequest(name="עצמאות"))
    sub_label = service.create_sub_label(SubLabelCreateRequest(label_id=label.id, name="היגיינה"))
    skill = service.create_skill(SkillCreateRequest(sub_label_id=sub_label.id, name="רחיצת ידיים"))
    service.create_solution(SolutionCreateRequest(skill_id=skill.id, text="תרגול יומי"))
    hidden = service.create_label(LabelCreateRequest(name="מוסתר"))
    service.update_label(hidden.id, LabelUpdateRequest(is_active=False))

    tree = service.active_tree()

    assert [node.name for node in tree] == ["עצמאות"]
    assert tree[0].sub_labels[0].skills[0].solutions[0].text == "תרגול יומי"


def test_deactivating_skill_removes_it_from_tree(db_session: Session) -> None:
    service = _service(db_session)
    label = service.create_label(LabelCreateRequest(name="עצמאות"))
    sub_label = service.create_sub_label(SubLabelCreateRequest(label_id=label.id, name="היגיינה"))
    skill = service.create_skill(SkillCreateRequest(sub_label_id=sub_label.id, name="רחיצת ידיים"))

    service.update_skill(skill.id, SkillUpdateRequest(is_active=False))

    tree = service.active_tree()
    assert tree[0].sub_labels[0].skills == []
