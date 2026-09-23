import logging
import uuid

from backend.app.client.institutions.institution_purge_repository import (
    InstitutionPurgeRepository,
)
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.utils.service.password_verifier import PasswordVerifier

_ENTITY_TYPE = "institution"
_logger = logging.getLogger(__name__)


class InstitutionPurgeService:
    def __init__(
        self,
        institutions: InstitutionRepository,
        purge_repository: InstitutionPurgeRepository,
        password_verifier: PasswordVerifier,
    ) -> None:
        self._institutions = institutions
        self._purge = purge_repository
        self._password_verifier = password_verifier

    def delete(self, institution_id: uuid.UUID, actor_id: uuid.UUID, password: str) -> None:
        self._password_verifier.verify(actor_id, password)
        institution = self._institutions.get(institution_id)
        if institution is None:
            raise NotFoundError(_ENTITY_TYPE)
        self._purge.purge(institution_id)
        _logger.info(
            "institution purged",
            extra={"institution_id": str(institution_id), "actor": str(actor_id)},
        )
