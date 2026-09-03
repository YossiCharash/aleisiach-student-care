import uuid

from sqlalchemy import select

from backend.app.client.database.ordered_node_repository import OrderedNodeRepository
from backend.app.models.client.diagnosis_catalog import DiagnosisCatalog


class DiagnosisCatalogRepository(OrderedNodeRepository):
    def add(self, entry: DiagnosisCatalog) -> DiagnosisCatalog:
        return self._add(entry)

    def get(self, diagnosis_id: uuid.UUID) -> DiagnosisCatalog | None:
        return self._get(DiagnosisCatalog, diagnosis_id)

    def get_by_name(self, name: str) -> DiagnosisCatalog | None:
        return self._session.scalar(select(DiagnosisCatalog).where(DiagnosisCatalog.name == name))

    def list(self, include_inactive: bool) -> list[DiagnosisCatalog]:
        return self._ordered(DiagnosisCatalog, include_inactive)

    def next_order(self) -> int:
        return self._next_order(DiagnosisCatalog)
