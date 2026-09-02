from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.auth.auth_token_repository import AuthTokenRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher_factory import InvitationDispatcherFactory
from backend.app.service.auth.invitation_service import InvitationService
from backend.app.service.auth.token_consumer import TokenConsumer


class InvitationServiceFactory:
    @staticmethod
    def create(session: Session, bootstrap: Bootstrap) -> InvitationService:
        tokens = AuthTokenRepository(session)
        return InvitationService(
            UserRepository(session),
            InvitationDispatcherFactory.create(session, bootstrap),
            TokenConsumer(tokens, bootstrap.token_factory),
            bootstrap.password_hasher,
            AuditLogger(AuditLogRepository(session)),
        )
