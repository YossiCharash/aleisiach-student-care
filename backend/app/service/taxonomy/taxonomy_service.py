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
from backend.app.schema.routes.label_update_request import LabelUpdateRequest
from backend.app.schema.routes.skill_create_request import SkillCreateRequest
from backend.app.schema.routes.skill_response import SkillResponse
from backend.app.schema.routes.skill_tree_node import SkillTreeNode
from backend.app.schema.routes.skill_update_request import SkillUpdateRequest
from backend.app.schema.routes.solution_create_request import SolutionCreateRequest
from backend.app.schema.routes.solution_response import SolutionResponse
from backend.app.schema.routes.solution_tree_node import SolutionTreeNode
from backend.app.schema.routes.solution_update_request import SolutionUpdateRequest
from backend.app.schema.routes.sub_label_create_request import SubLabelCreateRequest
from backend.app.schema.routes.sub_label_response import SubLabelResponse
from backend.app.schema.routes.sub_label_tree_node import SubLabelTreeNode
from backend.app.schema.routes.sub_label_update_request import SubLabelUpdateRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger

_ENTITY_TYPE = "taxonomy"


class TaxonomyService:
    def __init__(self, taxonomy_repository: TaxonomyRepository, audit_logger: AuditLogger) -> None:
        self._taxonomy = taxonomy_repository
        self._audit = audit_logger

    def _audit_change(
        self,
        actor_id: uuid.UUID,
        action: AuditAction,
        entity_id: uuid.UUID,
        changes: list[str],
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=entity_id,
                changes=changes,
            )
        )

    def list_labels(self, include_inactive: bool) -> list[LabelResponse]:
        labels = self._taxonomy.list_labels(include_inactive)
        return [LabelResponse.model_validate(label) for label in labels]

    def create_label(self, request: LabelCreateRequest, actor_id: uuid.UUID) -> LabelResponse:
        label = Label(name=request.name, order=self._taxonomy.next_label_order())
        self._taxonomy.add_label(label)
        self._audit_change(actor_id, AuditAction.CREATE, label.id, ["name"])
        return LabelResponse.model_validate(label)

    def update_label(
        self, label_id: uuid.UUID, request: LabelUpdateRequest, actor_id: uuid.UUID
    ) -> LabelResponse:
        label = self._taxonomy.get_label(label_id)
        if label is None:
            raise NotFoundError("label")
        self._apply_ordered_update(label, request.name, request.order, request.is_active)
        self._taxonomy.flush()
        self._audit_change(actor_id, AuditAction.UPDATE, label.id, self._ordered_changes(request))
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
        self._audit_change(actor_id, AuditAction.CREATE, sub_label.id, ["name"])
        return SubLabelResponse.model_validate(sub_label)

    def update_sub_label(
        self, sub_label_id: uuid.UUID, request: SubLabelUpdateRequest, actor_id: uuid.UUID
    ) -> SubLabelResponse:
        sub_label = self._taxonomy.get_sub_label(sub_label_id)
        if sub_label is None:
            raise NotFoundError("sub_label")
        self._apply_ordered_update(sub_label, request.name, request.order, request.is_active)
        self._taxonomy.flush()
        self._audit_change(
            actor_id, AuditAction.UPDATE, sub_label.id, self._ordered_changes(request)
        )
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
        self._audit_change(actor_id, AuditAction.CREATE, skill.id, ["name"])
        return SkillResponse.model_validate(skill)

    def update_skill(
        self, skill_id: uuid.UUID, request: SkillUpdateRequest, actor_id: uuid.UUID
    ) -> SkillResponse:
        skill = self._taxonomy.get_skill(skill_id)
        if skill is None:
            raise NotFoundError("skill")
        self._apply_ordered_update(skill, request.name, request.order, request.is_active)
        self._taxonomy.flush()
        self._audit_change(actor_id, AuditAction.UPDATE, skill.id, self._ordered_changes(request))
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
        self._audit_change(actor_id, AuditAction.CREATE, solution.id, ["text"])
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
        self._audit_change(actor_id, AuditAction.UPDATE, solution.id, changes)
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

    def _apply_ordered_update(
        self,
        node: Label | SubLabel | Skill,
        name: str | None,
        order: int | None,
        is_active: bool | None,
    ) -> None:
        if name is not None:
            node.name = name
        if order is not None:
            node.order = order
        if is_active is not None:
            node.is_active = is_active

    def _ordered_changes(
        self, request: LabelUpdateRequest | SubLabelUpdateRequest | SkillUpdateRequest
    ) -> list[str]:
        return [
            field
            for field, value in (
                ("name", request.name),
                ("order", request.order),
                ("is_active", request.is_active),
            )
            if value is not None
        ]
