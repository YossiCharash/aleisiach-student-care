import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus


class ClassRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def active_exists(self, class_id: uuid.UUID) -> bool:
        entity = self._session.get(ClassEntity, class_id)
        return entity is not None and not entity.is_archived

    def add(self, entity: ClassEntity) -> ClassEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def get(self, class_id: uuid.UUID) -> ClassEntity | None:
        return self._session.get(ClassEntity, class_id)

    def list_active(self) -> list[ClassEntity]:
        statement = (
            select(ClassEntity).where(ClassEntity.is_archived.is_(False)).order_by(ClassEntity.name)
        )
        return list(self._session.scalars(statement).all())

    def list_archived(self) -> list[ClassEntity]:
        statement = (
            select(ClassEntity).where(ClassEntity.is_archived.is_(True)).order_by(ClassEntity.name)
        )
        return list(self._session.scalars(statement).all())

    def count_active_students(self, class_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Student)
            .where(Student.class_id == class_id, Student.is_archived.is_(False))
        )
        return self._session.scalar(statement) or 0

    def count_enabled_users(self, class_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(User)
            .where(User.class_id == class_id, User.status != UserStatus.DISABLED)
        )
        return self._session.scalar(statement) or 0
