import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity


class ClassRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def exists(self, class_id: uuid.UUID) -> bool:
        return self._session.get(ClassEntity, class_id) is not None

    def add(self, entity: ClassEntity) -> ClassEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def get(self, class_id: uuid.UUID) -> ClassEntity | None:
        return self._session.get(ClassEntity, class_id)

    def list_all(self) -> list[ClassEntity]:
        statement = select(ClassEntity).order_by(ClassEntity.name)
        return list(self._session.scalars(statement).all())
