import uuid
from typing import TypeVar

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from backend.app.models.client.label import Label
from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.sub_label import SubLabel

NodeT = TypeVar("NodeT", bound=OrderedTaxonomyNode)


class TaxonomyRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def flush(self) -> None:
        self._session.flush()

    def add_label(self, label: Label) -> Label:
        return self._add(label)

    def get_label(self, label_id: uuid.UUID) -> Label | None:
        return self._session.get(Label, label_id)

    def list_labels(self, include_inactive: bool) -> list[Label]:
        return self._ordered(Label, include_inactive)

    def next_label_order(self) -> int:
        return self._next_order(Label)

    def add_sub_label(self, sub_label: SubLabel) -> SubLabel:
        return self._add(sub_label)

    def get_sub_label(self, sub_label_id: uuid.UUID) -> SubLabel | None:
        return self._session.get(SubLabel, sub_label_id)

    def list_sub_labels(self, label_id: uuid.UUID, include_inactive: bool) -> list[SubLabel]:
        return self._ordered(SubLabel, include_inactive, SubLabel.label_id == label_id)

    def next_sub_label_order(self, label_id: uuid.UUID) -> int:
        return self._next_order(SubLabel, SubLabel.label_id == label_id)

    def add_skill(self, skill: Skill) -> Skill:
        return self._add(skill)

    def get_skill(self, skill_id: uuid.UUID) -> Skill | None:
        return self._session.get(Skill, skill_id)

    def list_skills(self, sub_label_id: uuid.UUID, include_inactive: bool) -> list[Skill]:
        return self._ordered(Skill, include_inactive, Skill.sub_label_id == sub_label_id)

    def next_skill_order(self, sub_label_id: uuid.UUID) -> int:
        return self._next_order(Skill, Skill.sub_label_id == sub_label_id)

    def add_solution(self, solution: Solution) -> Solution:
        self._session.add(solution)
        self._session.flush()
        return solution

    def get_solution(self, solution_id: uuid.UUID) -> Solution | None:
        return self._session.get(Solution, solution_id)

    def list_solutions(self, skill_id: uuid.UUID, include_inactive: bool) -> list[Solution]:
        statement = select(Solution).where(Solution.skill_id == skill_id)
        if not include_inactive:
            statement = statement.where(Solution.is_active.is_(True))
        statement = statement.order_by(Solution.text)
        return list(self._session.scalars(statement).all())

    def active_labels(self) -> list[Label]:
        return self._ordered(Label, include_inactive=False)

    def active_sub_labels(self) -> list[SubLabel]:
        return self._ordered(SubLabel, include_inactive=False)

    def active_skills(self) -> list[Skill]:
        return self._ordered(Skill, include_inactive=False)

    def active_solutions(self) -> list[Solution]:
        statement = select(Solution).where(Solution.is_active.is_(True))
        return list(self._session.scalars(statement).all())

    def _add(self, node: NodeT) -> NodeT:
        self._session.add(node)
        self._session.flush()
        return node

    def _ordered(
        self, model: type[NodeT], include_inactive: bool, *filters: ColumnElement[bool]
    ) -> list[NodeT]:
        statement = select(model)
        for condition in filters:
            statement = statement.where(condition)
        if not include_inactive:
            statement = statement.where(model.is_active.is_(True))
        statement = statement.order_by(model.order, model.name)
        return list(self._session.scalars(statement).all())

    def _next_order(self, model: type[NodeT], *filters: ColumnElement[bool]) -> int:
        statement = select(func.coalesce(func.max(model.order), -1))
        for condition in filters:
            statement = statement.where(condition)
        current_max = self._session.scalar(statement)
        return int(current_max if current_max is not None else -1) + 1
