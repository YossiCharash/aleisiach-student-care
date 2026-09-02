from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.client.auth.session_repository import SessionRepository
from backend.app.client.database.provider import get_session
from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.errors.service.institution_inactive_error import InstitutionInactiveError
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.service.tenant_context import TenantContext
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
    user = UserRepository(session).get_account(user_id)
    if user is None or user.status != UserStatus.ACTIVE:
        raise AuthenticationError
    _apply_tenant_binding(session, user)
    return user


def _apply_tenant_binding(session: Session, user: User) -> None:
    if user.institution_id is None:
        TenantBinding.deny(session)
        return
    TenantBinding.bind(session, user.institution_id)


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_tenant(request: Request, user: CurrentUser, session: SessionDep) -> TenantContext:
    if user.institution_id is None:
        raise AuthorizationError
    institution = InstitutionRepository(session).get(user.institution_id)
    if institution is None:
        raise AuthorizationError
    request.state.institution_code = institution.code
    if not institution.is_active:
        raise InstitutionInactiveError
    return TenantContext(institution_id=institution.id, institution_name=institution.name)


Tenant = Annotated[TenantContext, Depends(require_tenant)]


def require_super_admin(user: CurrentUser) -> User:
    if user.role != UserRole.SUPER_ADMIN:
        raise AuthorizationError
    return user


SuperAdmin = Annotated[User, Depends(require_super_admin)]


def require_manager(user: CurrentUser, _: Tenant) -> User:
    if user.role != UserRole.MANAGER:
        raise AuthorizationError
    return user


Manager = Annotated[User, Depends(require_manager)]

_CONTENT_WRITER_ROLES = frozenset({UserRole.MANAGER, UserRole.INSTRUCTOR})


def require_content_writer(user: CurrentUser, _: Tenant) -> User:
    if user.role not in _CONTENT_WRITER_ROLES:
        raise AuthorizationError
    return user


ContentWriter = Annotated[User, Depends(require_content_writer)]

_SOCIAL_NOTE_READER_ROLES = frozenset({UserRole.MANAGER, UserRole.INSTRUCTOR})


def require_social_note_reader(user: CurrentUser, _: Tenant) -> User:
    if user.role not in _SOCIAL_NOTE_READER_ROLES:
        raise AuthorizationError
    return user


SocialNoteReader = Annotated[User, Depends(require_social_note_reader)]
