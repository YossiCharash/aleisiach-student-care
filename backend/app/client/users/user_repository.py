import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        if user.institution_id is None:
            user.institution_id = TenantBinding.require(self._session)
        self._session.add(user)
        self._session.flush()
        return user

    def commit(self) -> None:
        self._session.commit()

    def get(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id, populate_existing=True)

    def list_all(self) -> list[User]:
        return list(self._session.scalars(select(User).order_by(User.full_name)).all())

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(select(User).where(User.email == email))

    def list_active_by_email(self, email: str) -> list[User]:
        with TenantBinding.platform(self._session):
            statement = (
                select(User)
                .where(User.email == email, User.status == UserStatus.ACTIVE)
                .order_by(User.username)
            )
            return list(self._session.scalars(statement).all())

    def get_by_username(self, username: str) -> User | None:
        with TenantBinding.platform(self._session):
            return self._session.scalar(select(User).where(User.username == username))
