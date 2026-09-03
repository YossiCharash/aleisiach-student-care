from sqlalchemy.orm import Session

from backend.app.client.auth.session_repository import SessionRepository
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.service.auth.session_service import SessionService
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.support.seeding import seed_actor


def _service(session: Session) -> SessionService:
    return SessionService(SessionRepository(session), TokenFactory(), AuthSettings())


def test_create_then_resolve_returns_user_id(db_session: Session) -> None:
    service = _service(db_session)
    user_id = seed_actor(db_session)

    token = service.create(user_id)

    assert service.resolve(token) == user_id


def test_revoke_invalidates_session(db_session: Session) -> None:
    service = _service(db_session)
    token = service.create(seed_actor(db_session))

    service.revoke(token)

    assert service.resolve(token) is None


def test_resolve_unknown_token_returns_none(db_session: Session) -> None:
    assert _service(db_session).resolve("not-a-real-token") is None
