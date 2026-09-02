import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.institution import Institution


class InstitutionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, institution: Institution) -> Institution:
        self._session.add(institution)
        self._session.flush()
        return institution

    def get(self, institution_id: uuid.UUID) -> Institution | None:
        return self._session.get(Institution, institution_id)

    def get_by_code(self, code: str) -> Institution | None:
        return self._session.scalar(select(Institution).where(Institution.code == code))

    def list_all(self) -> list[Institution]:
        return list(self._session.scalars(select(Institution).order_by(Institution.name)).all())
