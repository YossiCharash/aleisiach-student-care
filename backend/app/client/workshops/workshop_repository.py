import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.models.client.workshop import Workshop


class WorkshopRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def active_exists(self, workshop_id: uuid.UUID) -> bool:
        entity = self._session.get(Workshop, workshop_id, populate_existing=True)
        return entity is not None and not entity.is_archived

    def add(self, entity: Workshop) -> Workshop:
        self._session.add(entity)
        self._session.flush()
        return entity

    def get(self, workshop_id: uuid.UUID) -> Workshop | None:
        return self._session.get(Workshop, workshop_id, populate_existing=True)

    def list_active(self) -> list[Workshop]:
        statement = select(Workshop).where(Workshop.is_archived.is_(False)).order_by(Workshop.name)
        return list(self._session.scalars(statement).all())

    def list_archived(self) -> list[Workshop]:
        statement = select(Workshop).where(Workshop.is_archived.is_(True)).order_by(Workshop.name)
        return list(self._session.scalars(statement).all())

    def list_instructors(self) -> list[User]:
        statement = (
            select(User)
            .where(User.role == UserRole.INSTRUCTOR, User.status != UserStatus.DISABLED)
            .order_by(User.full_name)
        )
        return list(self._session.scalars(statement).all())

    def get_instructor(self, user_id: uuid.UUID) -> User | None:
        user = self._session.get(User, user_id, populate_existing=True)
        if user is None or user.role is not UserRole.INSTRUCTOR:
            return None
        if user.status is UserStatus.DISABLED:
            return None
        return user

    def instructors_for(self, workshop_id: uuid.UUID) -> list[User]:
        statement = (
            select(User)
            .where(
                User.role == UserRole.INSTRUCTOR,
                User.status != UserStatus.DISABLED,
                User.workshop_id == workshop_id,
            )
            .order_by(User.full_name)
        )
        return list(self._session.scalars(statement).all())

    def instructors_by_workshop(self) -> dict[uuid.UUID, list[User]]:
        assigned: dict[uuid.UUID, list[User]] = {}
        for instructor in self.list_instructors():
            if instructor.workshop_id is not None:
                assigned.setdefault(instructor.workshop_id, []).append(instructor)
        return assigned

    def assign_instructors(
        self, workshop_id: uuid.UUID, instructor_ids: set[uuid.UUID]
    ) -> list[uuid.UUID]:
        affected: list[uuid.UUID] = []
        current = self._session.scalars(
            select(User).where(User.role == UserRole.INSTRUCTOR, User.workshop_id == workshop_id)
        ).all()
        for holder in current:
            if holder.id not in instructor_ids:
                holder.workshop_id = None
                affected.append(holder.id)
        for instructor_id in instructor_ids:
            chosen = self.get_instructor(instructor_id)
            if chosen is not None and chosen.workshop_id != workshop_id:
                chosen.workshop_id = workshop_id
                affected.append(chosen.id)
        self._session.flush()
        return affected

    def count_active_students(self, workshop_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Student)
            .where(
                Student.institution_id == TenantBinding.require(self._session),
                Student.workshop_id == workshop_id,
                Student.is_archived.is_(False),
            )
        )
        return self._session.scalar(statement) or 0

    def count_enabled_users(self, workshop_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(User)
            .where(
                User.institution_id == TenantBinding.require(self._session),
                User.workshop_id == workshop_id,
                User.status != UserStatus.DISABLED,
            )
        )
        return self._session.scalar(statement) or 0
