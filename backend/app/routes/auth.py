from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.database.provider import get_session
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.routes.security import (
    CredentialsDep,
    CurrentUser,
    Manager,
    build_session_service,
)
from backend.app.schema.routes.invitation_accept_request import InvitationAcceptRequest
from backend.app.schema.routes.login_request import LoginRequest
from backend.app.schema.routes.login_response import LoginResponse
from backend.app.schema.routes.password_change_request import PasswordChangeRequest
from backend.app.schema.routes.password_reset_confirm_request import PasswordResetConfirmRequest
from backend.app.schema.routes.password_reset_request import PasswordResetRequest
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.service.invitation_command import InvitationCommand
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.authentication_service import AuthenticationService
from backend.app.service.auth.invitation_service import InvitationService
from backend.app.service.auth.password_change_service import PasswordChangeService
from backend.app.service.auth.password_reset_service import PasswordResetService
from backend.app.service.auth.session_service import SessionService
from backend.app.service.auth.token_consumer import TokenConsumer
from backend.app.service.auth.token_issuer import TokenIssuer

SessionDep = Annotated[Session, Depends(get_session)]
BootstrapDep = Annotated[Bootstrap, Depends(get_bootstrap)]


def get_invitation_service(session: SessionDep, bootstrap: BootstrapDep) -> InvitationService:
    tokens = AuthTokenRepository(session)
    return InvitationService(
        UserRepository(session),
        TokenIssuer(tokens, bootstrap.token_factory),
        TokenConsumer(tokens, bootstrap.token_factory),
        bootstrap.password_hasher,
        bootstrap.email_sender,
        bootstrap.settings.auth,
        bootstrap.settings.email,
        AuditLogger(AuditLogRepository(session)),
    )


def get_authentication_service(
    session: SessionDep, bootstrap: BootstrapDep
) -> AuthenticationService:
    return AuthenticationService(
        UserRepository(session),
        bootstrap.password_hasher,
        bootstrap.settings.auth,
        bootstrap.clock,
    )


def get_password_change_service(
    session: SessionDep, bootstrap: BootstrapDep
) -> PasswordChangeService:
    return PasswordChangeService(UserRepository(session), bootstrap.password_hasher)


def get_password_reset_service(
    session: SessionDep, bootstrap: BootstrapDep
) -> PasswordResetService:
    tokens = AuthTokenRepository(session)
    return PasswordResetService(
        UserRepository(session),
        TokenIssuer(tokens, bootstrap.token_factory),
        TokenConsumer(tokens, bootstrap.token_factory),
        bootstrap.password_hasher,
        bootstrap.email_sender,
        bootstrap.settings.auth,
        bootstrap.settings.email,
        bootstrap.clock,
    )


def get_session_service(session: SessionDep, bootstrap: BootstrapDep) -> SessionService:
    return build_session_service(session, bootstrap)


InvitationDep = Annotated[InvitationService, Depends(get_invitation_service)]
AuthenticationDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
PasswordChangeDep = Annotated[PasswordChangeService, Depends(get_password_change_service)]
PasswordResetDep = Annotated[PasswordResetService, Depends(get_password_reset_service)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest, auth: AuthenticationDep, sessions: SessionServiceDep
) -> LoginResponse:
    user = auth.authenticate(request.username, request.password)
    token = sessions.create(user.id)
    return LoginResponse(token=token, user=user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(credentials: CredentialsDep, sessions: SessionServiceDep) -> None:
    if credentials is not None:
        sessions.revoke(credentials.credentials)


@router.post("/invitations", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(
    request: InvitationCommand, service: InvitationDep, manager: Manager
) -> UserResponse:
    return service.invite(request, manager.id)


@router.post("/invitations/accept", response_model=UserResponse)
def accept_invitation(request: InvitationAcceptRequest, service: InvitationDep) -> UserResponse:
    return service.accept(request.token, request.username, request.password)


@router.post("/password/change", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    request: PasswordChangeRequest, service: PasswordChangeDep, user: CurrentUser
) -> None:
    service.change(user.id, request.current_password, request.new_password)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(request: PasswordResetRequest, service: PasswordResetDep) -> None:
    service.request(request.email)


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(request: PasswordResetConfirmRequest, service: PasswordResetDep) -> None:
    service.reset(request.token, request.new_password)
