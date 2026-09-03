import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from backend.app.errors.service.authorization_error import AuthorizationError

_KEY = "institution_id"
_DENY_ALL = uuid.UUID(int=0)


class TenantBinding:
    @staticmethod
    def bind(session: Session, institution_id: uuid.UUID) -> None:
        session.info[_KEY] = institution_id

    @staticmethod
    def deny(session: Session) -> None:
        session.info[_KEY] = _DENY_ALL

    @staticmethod
    def filter_value(session: Session) -> uuid.UUID | None:
        bound = session.info.get(_KEY)
        return bound if isinstance(bound, uuid.UUID) else None

    @staticmethod
    def current(session: Session) -> uuid.UUID | None:
        bound = TenantBinding.filter_value(session)
        return None if bound == _DENY_ALL else bound

    @staticmethod
    def require(session: Session) -> uuid.UUID:
        bound = TenantBinding.current(session)
        if bound is None:
            raise AuthorizationError
        return bound

    @staticmethod
    @contextmanager
    def platform(session: Session) -> Iterator[None]:
        previous = session.info.pop(_KEY, None)
        try:
            yield
        finally:
            if previous is not None:
                session.info[_KEY] = previous
