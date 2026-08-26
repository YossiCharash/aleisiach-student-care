from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.database.provider import get_session
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.service.auth.session_service import SessionService

_bearer = HTTPBearer(auto_error=False)

CredentialsDep = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]
SessionDep = Annotated[Session, Depends(get_session)]
BootstrapDep = Annotated[Bootstrap, Depends(get_bootstrap)]


def build_session_service(session: Session, bootstrap: Bootstrap) -> SessionService:
    return SessionService(
        SessionRepository(session),
        bootstrap.token_factory,
        bootstrap.settings.auth,
    )


def get_current_user(
    credentials: CredentialsDep,
    session: SessionDep,
    bootstrap: BootstrapDep,
) -> User:
    if credentials is None:
        raise AuthenticationError
    user_id = build_session_service(session, bootstrap).resolve(credentials.credentials)
    if user_id is None:
        raise AuthenticationError
    user = UserRepository(session).get(user_id)
    if user is None:
        raise AuthenticationError
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_manager(user: CurrentUser) -> User:
    if user.role != UserRole.MANAGER:
        raise AuthorizationError
    return user


Manager = Annotated[User, Depends(require_manager)]

_CONTENT_WRITER_ROLES = frozenset({UserRole.MANAGER, UserRole.INSTRUCTOR})


def require_content_writer(user: CurrentUser) -> User:
    if user.role not in _CONTENT_WRITER_ROLES:
        raise AuthorizationError
    return user


ContentWriter = Annotated[User, Depends(require_content_writer)]

_SOCIAL_NOTE_READER_ROLES = frozenset({UserRole.MANAGER, UserRole.INSTRUCTOR})


def require_social_note_reader(user: CurrentUser) -> User:
    if user.role not in _SOCIAL_NOTE_READER_ROLES:
        raise AuthorizationError
    return user


SocialNoteReader = Annotated[User, Depends(require_social_note_reader)]
