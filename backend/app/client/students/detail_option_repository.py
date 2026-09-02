import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.detail_option_field import DetailOptionField


class DetailOptionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, option: DetailOption) -> DetailOption:
        self._session.add(option)
        self._session.flush()
        return option

    def get(self, option_id: uuid.UUID) -> DetailOption | None:
        return self._session.get(DetailOption, option_id, populate_existing=True)

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
        statement = select(func.coalesce(func.max(DetailOption.order), -1)).where(
            DetailOption.institution_id == TenantBinding.require(self._session),
            DetailOption.field == field,
        )
        current_max = self._session.scalar(statement)
        return int(current_max if current_max is not None else -1) + 1

    def flush(self) -> None:
        self._session.flush()
