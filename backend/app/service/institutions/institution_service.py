import uuid
from datetime import UTC, datetime

from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.institution import Institution
from backend.app.schema.routes.institution_response import InstitutionResponse
from backend.app.schema.routes.institution_summary import InstitutionSummary
from backend.app.schema.routes.institution_update_request import InstitutionUpdateRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger

_ENTITY_TYPE = "institution"


class InstitutionService:
    def __init__(self, institutions: InstitutionRepository, audit_logger: AuditLogger) -> None:
        self._institutions = institutions
        self._audit = audit_logger

    def list_institutions(self) -> list[InstitutionSummary]:
        counts = self._institutions.counts()
        invited = self._institutions.invited_managers()
        summaries: list[InstitutionSummary] = []
        for institution in self._institutions.list_all():
            found = counts.get(institution.id)
            manager = invited.get(institution.id)
            summaries.append(
                InstitutionSummary(
                    **InstitutionResponse.model_validate(institution).model_dump(),
                    user_count=found.user_count if found else 0,
                    student_count=found.student_count if found else 0,
                    pending_manager_email=None if manager is None else manager.email,
                )
            )
        return summaries

    def get(self, institution_id: uuid.UUID) -> InstitutionResponse:
        return InstitutionResponse.model_validate(self._require(institution_id))

    def update(
        self, institution_id: uuid.UUID, request: InstitutionUpdateRequest, actor_id: uuid.UUID
    ) -> InstitutionResponse:
        institution = self._require(institution_id)
        changes = self._apply(institution, request)
        if changes:
            self._record(actor_id, AuditAction.UPDATE, institution.id, changes)
        return InstitutionResponse.model_validate(institution)

    @staticmethod
    def _apply(institution: Institution, request: InstitutionUpdateRequest) -> list[str]:
        changes: list[str] = []
        if institution.name != request.name:
            institution.name = request.name
            changes.append("name")
        if institution.contact_name != request.contact_name:
            institution.contact_name = request.contact_name
            changes.append("contact_name")
        if institution.contact_phone != request.contact_phone:
            institution.contact_phone = request.contact_phone
            changes.append("contact_phone")
        return changes

    def deactivate(self, institution_id: uuid.UUID, actor_id: uuid.UUID) -> InstitutionResponse:
        institution = self._require(institution_id)
        if institution.is_active:
            institution.is_active = False
            institution.deactivated_at = datetime.now(UTC)
            institution.deactivated_by = actor_id
            self._record(actor_id, AuditAction.ARCHIVE, institution.id, ["is_active"])
        return InstitutionResponse.model_validate(institution)

    def activate(self, institution_id: uuid.UUID, actor_id: uuid.UUID) -> InstitutionResponse:
        institution = self._require(institution_id)
        if not institution.is_active:
            institution.is_active = True
            institution.deactivated_at = None
            institution.deactivated_by = None
            self._record(actor_id, AuditAction.UPDATE, institution.id, ["is_active"])
        return InstitutionResponse.model_validate(institution)

    def _require(self, institution_id: uuid.UUID) -> Institution:
        institution = self._institutions.get(institution_id)
        if institution is None:
            raise NotFoundError(_ENTITY_TYPE)
        return institution

    def _record(
        self, actor_id: uuid.UUID, action: AuditAction, entity_id: uuid.UUID, changes: list[str]
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=entity_id,
                changes=changes,
            )
        )
