import uuid

from backend.app.client.database.tenant_scope import TenantScope
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.errors.service.institution_code_taken_error import InstitutionCodeTakenError
from backend.app.errors.service.no_pending_manager_invitation_error import (
    NoPendingManagerInvitationError,
)
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.institution import Institution
from backend.app.models.client.user_role import UserRole
from backend.app.schema.routes.institution_response import InstitutionResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.institution_provisioning_command import (
    InstitutionProvisioningCommand,
)
from backend.app.schema.service.invitation_command import InvitationCommand
from backend.app.seed.institution_template_seeder import InstitutionTemplateSeeder
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher
from backend.app.service.auth.invitation_service import InvitationService

_ENTITY_TYPE = "institution"
_PERMISSION_ENTITY_TYPE = "permission"


class InstitutionProvisioningService:
    def __init__(
        self,
        institutions: InstitutionRepository,
        tenant_scope: TenantScope,
        template_seeder: InstitutionTemplateSeeder,
        invitations: InvitationService,
        dispatcher: InvitationDispatcher,
        audit_logger: AuditLogger,
    ) -> None:
        self._institutions = institutions
        self._scope = tenant_scope
        self._template = template_seeder
        self._invitations = invitations
        self._dispatcher = dispatcher
        self._audit = audit_logger

    def provision(
        self, command: InstitutionProvisioningCommand, actor_id: uuid.UUID
    ) -> InstitutionResponse:
        if self._institutions.get_by_code(command.code) is not None:
            raise InstitutionCodeTakenError
        institution = self._institutions.add(
            Institution(
                name=command.name,
                code=command.code,
                is_active=True,
                contact_name=command.contact_name,
                contact_phone=command.contact_phone,
            )
        )
        with self._scope.use(institution.id):
            self._template.seed(institution.id)
            self._invitations.invite(
                InvitationCommand(
                    full_name=command.manager_full_name,
                    email=command.manager_email,
                    role=UserRole.MANAGER,
                ),
                actor_id,
            )
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=institution.id,
                changes=["name", "code"],
            )
        )
        return InstitutionResponse.model_validate(institution)

    def resend_manager_invitation(
        self, institution_id: uuid.UUID, actor_id: uuid.UUID
    ) -> InstitutionResponse:
        institution = self._institutions.get(institution_id)
        if institution is None:
            raise NotFoundError(_ENTITY_TYPE)
        manager = self._institutions.invited_manager(institution_id)
        if manager is None:
            raise NoPendingManagerInvitationError
        self._dispatcher.dispatch(manager.id, manager.email)
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.CREATE,
                entity_type=_PERMISSION_ENTITY_TYPE,
                entity_id=manager.id,
                changes=["invitation"],
            )
        )
        return InstitutionResponse.model_validate(institution)
