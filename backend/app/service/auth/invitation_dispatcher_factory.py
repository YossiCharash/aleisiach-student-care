from sqlalchemy.orm import Session

from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher
from backend.app.service.auth.token_issuer import TokenIssuer


class InvitationDispatcherFactory:
    @staticmethod
    def create(session: Session, bootstrap: Bootstrap) -> InvitationDispatcher:
        tokens = AuthTokenRepository(session)
        return InvitationDispatcher(
            tokens,
            TokenIssuer(tokens, bootstrap.token_factory),
            bootstrap.email_sender,
            bootstrap.settings.auth,
            bootstrap.settings.email,
        )
