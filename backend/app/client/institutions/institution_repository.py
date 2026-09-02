import uuid

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.institution import Institution
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.service.institution_counts import InstitutionCounts

TenantColumn = InstrumentedAttribute[uuid.UUID] | InstrumentedAttribute[uuid.UUID | None]


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

    def counts(self) -> dict[uuid.UUID, InstitutionCounts]:
        with TenantBinding.platform(self._session):
            users = self._grouped_count(User.institution_id)
            students = self._grouped_count(Student.institution_id, Student.is_archived.is_(False))
        return {
            institution_id: InstitutionCounts(
                institution_id=institution_id,
                user_count=users.get(institution_id, 0),
                student_count=students.get(institution_id, 0),
            )
            for institution_id in users.keys() | students.keys()
        }

    def invited_managers(self) -> dict[uuid.UUID, User]:
        with TenantBinding.platform(self._session):
            statement = (
                select(User)
                .where(
                    User.role == UserRole.MANAGER,
                    User.status == UserStatus.INVITED,
                    User.institution_id.is_not(None),
                )
                .order_by(User.email.desc())
            )
            found = self._session.scalars(statement).all()
        return {manager.institution_id: manager for manager in found if manager.institution_id}

    def invited_manager(self, institution_id: uuid.UUID) -> User | None:
        return self.invited_managers().get(institution_id)

    def _grouped_count(
        self, column: TenantColumn, *filters: ColumnElement[bool]
    ) -> dict[uuid.UUID, int]:
        statement = select(column, func.count()).where(column.is_not(None)).group_by(column)
        for condition in filters:
            statement = statement.where(condition)
        return {row[0]: row[1] for row in self._session.execute(statement)}
