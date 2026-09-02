import uuid

from backend.app.client.database.tenant_scope import TenantScope
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.errors.service.institution_code_taken_error import InstitutionCodeTakenError
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
from backend.app.service.auth.invitation_service import InvitationService

_ENTITY_TYPE = "institution"


class InstitutionProvisioningService:
    def __init__(
        self,
        institutions: InstitutionRepository,
        tenant_scope: TenantScope,
        template_seeder: InstitutionTemplateSeeder,
        invitations: InvitationService,
        audit_logger: AuditLogger,
    ) -> None:
        self._institutions = institutions
        self._scope = tenant_scope
        self._template = template_seeder
        self._invitations = invitations
        self._audit = audit_logger

    def provision(
        self, command: InstitutionProvisioningCommand, actor_id: uuid.UUID
    ) -> InstitutionResponse:
        if self._institutions.get_by_code(command.code) is not None:
            raise InstitutionCodeTakenError
        institution = self._institutions.add(
            Institution(name=command.name, code=command.code, is_active=True)
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
