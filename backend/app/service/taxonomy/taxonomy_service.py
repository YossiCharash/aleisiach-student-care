import uuid
from collections import defaultdict

from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.label import Label
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.sub_label import SubLabel
from backend.app.schema.routes.label_create_request import LabelCreateRequest
from backend.app.schema.routes.label_response import LabelResponse
from backend.app.schema.routes.label_tree_node import LabelTreeNode
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.schema.routes.skill_create_request import SkillCreateRequest
from backend.app.schema.routes.skill_response import SkillResponse
from backend.app.schema.routes.skill_tree_node import SkillTreeNode
from backend.app.schema.routes.solution_create_request import SolutionCreateRequest
from backend.app.schema.routes.solution_response import SolutionResponse
from backend.app.schema.routes.solution_tree_node import SolutionTreeNode
from backend.app.schema.routes.solution_update_request import SolutionUpdateRequest
from backend.app.schema.routes.sub_label_create_request import SubLabelCreateRequest
from backend.app.schema.routes.sub_label_response import SubLabelResponse
from backend.app.schema.routes.sub_label_tree_node import SubLabelTreeNode
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.utils.service.ordered_node_updater import OrderedNodeUpdater

_ENTITY_TYPE = "taxonomy"


class TaxonomyService:
    def __init__(self, taxonomy_repository: TaxonomyRepository, audit_logger: AuditLogger) -> None:
        self._taxonomy = taxonomy_repository
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)

    def list_labels(self, include_inactive: bool) -> list[LabelResponse]:
        labels = self._taxonomy.list_labels(include_inactive)
        return [LabelResponse.model_validate(label) for label in labels]

    def create_label(self, request: LabelCreateRequest, actor_id: uuid.UUID) -> LabelResponse:
        label = Label(name=request.name, order=self._taxonomy.next_label_order())
        self._taxonomy.add_label(label)
        self._audit.record(actor_id, AuditAction.CREATE, label.id, ["name"])
        return LabelResponse.model_validate(label)

    def update_label(
        self, label_id: uuid.UUID, request: OrderedNodeUpdateRequest, actor_id: uuid.UUID
    ) -> LabelResponse:
        label = self._taxonomy.get_label(label_id)
        if label is None:
            raise NotFoundError("label")
        changes = OrderedNodeUpdater.apply(label, request)
        self._taxonomy.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, label.id, changes)
        return LabelResponse.model_validate(label)

    def list_sub_labels(
        self, label_id: uuid.UUID, include_inactive: bool
    ) -> list[SubLabelResponse]:
        if self._taxonomy.get_label(label_id) is None:
            raise NotFoundError("label")
        sub_labels = self._taxonomy.list_sub_labels(label_id, include_inactive)
        return [SubLabelResponse.model_validate(sub_label) for sub_label in sub_labels]

    def create_sub_label(
        self, request: SubLabelCreateRequest, actor_id: uuid.UUID
    ) -> SubLabelResponse:
        if self._taxonomy.get_label(request.label_id) is None:
            raise NotFoundError("label")
        sub_label = SubLabel(
            label_id=request.label_id,
            name=request.name,
            order=self._taxonomy.next_sub_label_order(request.label_id),
        )
        self._taxonomy.add_sub_label(sub_label)
        self._audit.record(actor_id, AuditAction.CREATE, sub_label.id, ["name"])
        return SubLabelResponse.model_validate(sub_label)

    def update_sub_label(
        self, sub_label_id: uuid.UUID, request: OrderedNodeUpdateRequest, actor_id: uuid.UUID
    ) -> SubLabelResponse:
        sub_label = self._taxonomy.get_sub_label(sub_label_id)
        if sub_label is None:
            raise NotFoundError("sub_label")
        changes = OrderedNodeUpdater.apply(sub_label, request)
        self._taxonomy.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, sub_label.id, changes)
        return SubLabelResponse.model_validate(sub_label)

    def list_skills(self, sub_label_id: uuid.UUID, include_inactive: bool) -> list[SkillResponse]:
        if self._taxonomy.get_sub_label(sub_label_id) is None:
            raise NotFoundError("sub_label")
        skills = self._taxonomy.list_skills(sub_label_id, include_inactive)
        return [SkillResponse.model_validate(skill) for skill in skills]

    def create_skill(self, request: SkillCreateRequest, actor_id: uuid.UUID) -> SkillResponse:
        if self._taxonomy.get_sub_label(request.sub_label_id) is None:
            raise NotFoundError("sub_label")
        skill = Skill(
            sub_label_id=request.sub_label_id,
            name=request.name,
            order=self._taxonomy.next_skill_order(request.sub_label_id),
        )
        self._taxonomy.add_skill(skill)
        self._audit.record(actor_id, AuditAction.CREATE, skill.id, ["name"])
        return SkillResponse.model_validate(skill)

    def update_skill(
        self, skill_id: uuid.UUID, request: OrderedNodeUpdateRequest, actor_id: uuid.UUID
    ) -> SkillResponse:
        skill = self._taxonomy.get_skill(skill_id)
        if skill is None:
            raise NotFoundError("skill")
        changes = OrderedNodeUpdater.apply(skill, request)
        self._taxonomy.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, skill.id, changes)
        return SkillResponse.model_validate(skill)

    def list_solutions(self, skill_id: uuid.UUID, include_inactive: bool) -> list[SolutionResponse]:
        if self._taxonomy.get_skill(skill_id) is None:
            raise NotFoundError("skill")
        solutions = self._taxonomy.list_solutions(skill_id, include_inactive)
        return [SolutionResponse.model_validate(solution) for solution in solutions]

    def create_solution(
        self, request: SolutionCreateRequest, actor_id: uuid.UUID
    ) -> SolutionResponse:
        if self._taxonomy.get_skill(request.skill_id) is None:
            raise NotFoundError("skill")
        solution = Solution(skill_id=request.skill_id, text=request.text)
        self._taxonomy.add_solution(solution)
        self._audit.record(actor_id, AuditAction.CREATE, solution.id, ["text"])
        return SolutionResponse.model_validate(solution)

    def update_solution(
        self, solution_id: uuid.UUID, request: SolutionUpdateRequest, actor_id: uuid.UUID
    ) -> SolutionResponse:
        solution = self._taxonomy.get_solution(solution_id)
        if solution is None:
            raise NotFoundError("solution")
        changes: list[str] = []
        if request.text is not None:
            solution.text = request.text
            changes.append("text")
        if request.is_active is not None:
            solution.is_active = request.is_active
            changes.append("is_active")
        self._taxonomy.flush()
        self._audit.record(actor_id, AuditAction.UPDATE, solution.id, changes)
        return SolutionResponse.model_validate(solution)

    def active_tree(self) -> list[LabelTreeNode]:
        sub_labels_by_label: dict[uuid.UUID, list[SubLabel]] = defaultdict(list)
        for sub_label in self._taxonomy.active_sub_labels():
            sub_labels_by_label[sub_label.label_id].append(sub_label)

        skills_by_sub_label: dict[uuid.UUID, list[Skill]] = defaultdict(list)
        for skill in self._taxonomy.active_skills():
            skills_by_sub_label[skill.sub_label_id].append(skill)

        solutions_by_skill: dict[uuid.UUID, list[Solution]] = defaultdict(list)
        for solution in self._taxonomy.active_solutions():
            solutions_by_skill[solution.skill_id].append(solution)

        return [
            LabelTreeNode(
                id=label.id,
                name=label.name,
                sub_labels=[
                    SubLabelTreeNode(
                        id=sub_label.id,
                        name=sub_label.name,
                        skills=[
                            SkillTreeNode(
                                id=skill.id,
                                name=skill.name,
                                solutions=[
                                    SolutionTreeNode(id=solution.id, text=solution.text)
                                    for solution in solutions_by_skill[skill.id]
                                ],
                            )
                            for skill in skills_by_sub_label[sub_label.id]
                        ],
                    )
                    for sub_label in sub_labels_by_label[label.id]
                ],
            )
            for label in self._taxonomy.active_labels()
        ]
