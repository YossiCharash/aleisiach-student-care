import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding


class TenantScope:
    def __init__(self, session: Session) -> None:
        self._session = session

    @contextmanager
    def use(self, institution_id: uuid.UUID) -> Iterator[None]:
        previous = TenantBinding.filter_value(self._session)
        TenantBinding.bind(self._session, institution_id)
        try:
            yield
        finally:
            if previous is None:
                TenantBinding.deny(self._session)
            else:
                TenantBinding.bind(self._session, previous)
