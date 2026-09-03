from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.client.database.tenant_filter import TenantFilter
from backend.app.configuration.database.database_settings import DatabaseSettings


class Database:
    def __init__(self, settings: DatabaseSettings) -> None:
        TenantFilter.register()
        self._engine: Engine = create_engine(settings.url, echo=settings.echo, future=True)
        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=self._engine, autoflush=False, expire_on_commit=False
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def session(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
