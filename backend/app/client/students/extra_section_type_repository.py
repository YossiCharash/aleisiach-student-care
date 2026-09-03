import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.extra_section_type import ExtraSectionType


class ExtraSectionTypeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, section_type: ExtraSectionType) -> ExtraSectionType:
        self._session.add(section_type)
        self._session.flush()
        return section_type

    def get(self, section_type_id: uuid.UUID) -> ExtraSectionType | None:
        return self._session.get(ExtraSectionType, section_type_id, populate_existing=True)

    def list(self, include_inactive: bool) -> list[ExtraSectionType]:
        statement = select(ExtraSectionType)
        if not include_inactive:
            statement = statement.where(ExtraSectionType.is_active.is_(True))
        statement = statement.order_by(ExtraSectionType.order, ExtraSectionType.name)
        return list(self._session.scalars(statement).all())

    def next_order(self, parent_id: uuid.UUID | None) -> int:
        statement = select(func.coalesce(func.max(ExtraSectionType.order), -1)).where(
            ExtraSectionType.institution_id == TenantBinding.require(self._session)
        )
        if parent_id is None:
            statement = statement.where(ExtraSectionType.parent_id.is_(None))
        else:
            statement = statement.where(ExtraSectionType.parent_id == parent_id)
        current_max = self._session.scalar(statement)
        return int(current_max if current_max is not None else -1) + 1

    def flush(self) -> None:
        self._session.flush()
