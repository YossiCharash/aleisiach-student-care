import uuid
from typing import TypeVar

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.base import Base
from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode

EntityT = TypeVar("EntityT", bound=Base)
NodeT = TypeVar("NodeT", bound=OrderedTaxonomyNode)


class OrderedNodeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def flush(self) -> None:
        self._session.flush()

    def _add(self, entity: EntityT) -> EntityT:
        self._session.add(entity)
        self._session.flush()
        return entity

    def _get(self, model: type[EntityT], entity_id: uuid.UUID) -> EntityT | None:
        return self._session.get(model, entity_id, populate_existing=True)

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
        statement = select(func.coalesce(func.max(model.order), -1)).where(
            model.institution_id == TenantBinding.require(self._session)
        )
        for condition in filters:
            statement = statement.where(condition)
        current_max = self._session.scalar(statement)
        return int(current_max if current_max is not None else -1) + 1
