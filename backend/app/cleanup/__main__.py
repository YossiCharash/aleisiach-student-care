from collections.abc import Iterator

from sqlalchemy.orm import Session

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.database.database import Database
from backend.app.configuration.settings import Settings
from backend.app.schema.service.cleanup_result import CleanupResult
from backend.app.service.maintenance.expired_credential_cleanup_service import (
    ExpiredCredentialCleanupService,
)
from backend.app.utils.service.clock import Clock


def main() -> None:
    settings = Settings()
    database = Database(settings.database)
    generator = database.session()
    session = next(generator)
    result = _run(session, generator, settings)
    print(f"נמחקו {result.sessions_deleted} sessions ו-{result.tokens_deleted} טוקנים שפג תוקפם.")


def _run(session: Session, generator: Iterator[Session], settings: Settings) -> CleanupResult:
    service = ExpiredCredentialCleanupService(
        SessionRepository(session),
        AuthTokenRepository(session),
        settings.retention,
        Clock(),
    )
    try:
        return service.run()
    except BaseException:
        session.rollback()
        raise
    finally:
        next(generator, None)


if __name__ == "__main__":
    main()
