import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        return user

    def commit(self) -> None:
        self._session.commit()

    def get(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id)

    def list_all(self) -> list[User]:
        return list(self._session.scalars(select(User).order_by(User.full_name)).all())

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(select(User).where(User.email == email))

    def get_by_username(self, username: str) -> User | None:
        return self._session.scalar(select(User).where(User.username == username))
