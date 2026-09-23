import logging
import uuid

from backend.app.client.institutions.institution_purge_repository import (
    InstitutionPurgeRepository,
)
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.utils.service.password_hasher import PasswordHasher

_ENTITY_TYPE = "institution"
_logger = logging.getLogger(__name__)


class InstitutionPurgeService:
    def __init__(
        self,
        institutions: InstitutionRepository,
        purge_repository: InstitutionPurgeRepository,
        users: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._institutions = institutions
        self._purge = purge_repository
        self._users = users
        self._password_hasher = password_hasher

    def delete(self, institution_id: uuid.UUID, actor_id: uuid.UUID, password: str) -> None:
        self._verify_password(actor_id, password)
        institution = self._institutions.get(institution_id)
        if institution is None:
            raise NotFoundError(_ENTITY_TYPE)
        self._purge.purge(institution_id)
        _logger.info(
            "institution purged",
            extra={"institution_id": str(institution_id), "actor": str(actor_id)},
        )

    def _verify_password(self, actor_id: uuid.UUID, password: str) -> None:
        actor = self._users.get_account(actor_id)
        if actor is None or actor.password_hash is None:
            raise AuthenticationError
        if not self._password_hasher.verify(actor.password_hash, password):
            raise InvalidCurrentPasswordError
