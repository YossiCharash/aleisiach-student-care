import uuid

from sqlalchemy.orm import Session

from app.models.client.class_entity import ClassEntity


class ClassRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def exists(self, class_id: uuid.UUID) -> bool:
        return self._session.get(ClassEntity, class_id) is not None
