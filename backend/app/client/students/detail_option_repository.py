import uuid

from sqlalchemy import select

from backend.app.client.database.ordered_node_repository import OrderedNodeRepository
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.detail_option_field import DetailOptionField


class DetailOptionRepository(OrderedNodeRepository):
    def add(self, option: DetailOption) -> DetailOption:
        return self._add(option)

    def get(self, option_id: uuid.UUID) -> DetailOption | None:
        return self._get(DetailOption, option_id)

    def get_by_field_and_name(self, field: DetailOptionField, name: str) -> DetailOption | None:
        statement = select(DetailOption).where(
            DetailOption.field == field, DetailOption.name == name
        )
        return self._session.scalar(statement)

    def list(self, include_inactive: bool) -> list[DetailOption]:
        statement = select(DetailOption)
        if not include_inactive:
            statement = statement.where(DetailOption.is_active.is_(True))
        statement = statement.order_by(DetailOption.field, DetailOption.order, DetailOption.name)
        return list(self._session.scalars(statement).all())

    def next_order(self, field: DetailOptionField) -> int:
        return self._next_order(DetailOption, DetailOption.field == field)
