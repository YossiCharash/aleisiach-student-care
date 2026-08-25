from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.client.auth.auth_token_repository import AuthTokenRepository
from app.client.database.provider import get_session
from app.client.users.user_repository import UserRepository
from app.configuration.bootstrap import Bootstrap
from app.configuration.provider import get_bootstrap
from app.schema.routes.invitation_accept_request import InvitationAcceptRequest
from app.schema.routes.login_request import LoginRequest
from app.schema.routes.password_reset_confirm_request import PasswordResetConfirmRequest
from app.schema.routes.password_reset_request import PasswordResetRequest
from app.schema.routes.user_response import UserResponse
from app.service.auth.authentication_service import AuthenticationService
from app.service.auth.invitation_service import InvitationService
from app.service.auth.password_reset_service import PasswordResetService
from app.service.auth.token_consumer import TokenConsumer
from app.service.auth.token_issuer import TokenIssuer

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
    )


def get_authentication_service(
    session: SessionDep, bootstrap: BootstrapDep
) -> AuthenticationService:
    return AuthenticationService(UserRepository(session), bootstrap.password_hasher)


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
    )


InvitationDep = Annotated[InvitationService, Depends(get_invitation_service)]
AuthenticationDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
PasswordResetDep = Annotated[PasswordResetService, Depends(get_password_reset_service)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(request: LoginRequest, service: AuthenticationDep) -> UserResponse:
    return service.authenticate(request.username, request.password)


@router.post("/invitations/accept", response_model=UserResponse)
def accept_invitation(request: InvitationAcceptRequest, service: InvitationDep) -> UserResponse:
    return service.accept(request.token, request.username, request.password)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(request: PasswordResetRequest, service: PasswordResetDep) -> None:
    service.request(request.email)


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(request: PasswordResetConfirmRequest, service: PasswordResetDep) -> None:
    service.reset(request.token, request.new_password)
