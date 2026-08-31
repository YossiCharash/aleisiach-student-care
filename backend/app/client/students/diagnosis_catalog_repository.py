import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.client.diagnosis_catalog import DiagnosisCatalog


class DiagnosisCatalogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: DiagnosisCatalog) -> DiagnosisCatalog:
        self._session.add(entry)
        self._session.flush()
        return entry

    def get(self, diagnosis_id: uuid.UUID) -> DiagnosisCatalog | None:
        return self._session.get(DiagnosisCatalog, diagnosis_id)

    def get_by_name(self, name: str) -> DiagnosisCatalog | None:
        statement = select(DiagnosisCatalog).where(DiagnosisCatalog.name == name)
        return self._session.scalar(statement)

    def list(self, include_inactive: bool) -> list[DiagnosisCatalog]:
        statement = select(DiagnosisCatalog)
        if not include_inactive:
            statement = statement.where(DiagnosisCatalog.is_active.is_(True))
        statement = statement.order_by(DiagnosisCatalog.order, DiagnosisCatalog.name)
        return list(self._session.scalars(statement).all())

    def next_order(self) -> int:
        statement = select(func.coalesce(func.max(DiagnosisCatalog.order), -1))
        current_max = self._session.scalar(statement)
        return int(current_max if current_max is not None else -1) + 1

    def flush(self) -> None:
        self._session.flush()
