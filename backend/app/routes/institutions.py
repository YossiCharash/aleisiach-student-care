import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.database.tenant_scope import TenantScope
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.client.students.detail_option_repository import DetailOptionRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.institutions.institution_template_settings import (
    InstitutionTemplateSettings,
)
from backend.app.configuration.provider import get_bootstrap
from backend.app.routes.security import SuperAdmin, require_super_admin
from backend.app.schema.routes.institution_create_request import InstitutionCreateRequest
from backend.app.schema.routes.institution_response import InstitutionResponse
from backend.app.schema.routes.institution_summary import InstitutionSummary
from backend.app.schema.routes.institution_update_request import InstitutionUpdateRequest
from backend.app.schema.service.institution_provisioning_command import (
    InstitutionProvisioningCommand,
)
from backend.app.seed.institution_template_seeder import InstitutionTemplateSeeder
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher_factory import InvitationDispatcherFactory
from backend.app.service.auth.invitation_service_factory import InvitationServiceFactory
from backend.app.service.institutions.institution_provisioning_service import (
    InstitutionProvisioningService,
)
from backend.app.service.institutions.institution_service import InstitutionService

SessionDep = Annotated[Session, Depends(get_session)]
BootstrapDep = Annotated[Bootstrap, Depends(get_bootstrap)]


def get_institution_service(session: SessionDep) -> InstitutionService:
    return InstitutionService(
        InstitutionRepository(session), AuditLogger(AuditLogRepository(session))
    )


def get_provisioning_service(
    session: SessionDep, bootstrap: BootstrapDep
) -> InstitutionProvisioningService:
    return InstitutionProvisioningService(
        InstitutionRepository(session),
        TenantScope(session),
        InstitutionTemplateSeeder(DetailOptionRepository(session), InstitutionTemplateSettings()),
        InvitationServiceFactory.create(session, bootstrap),
        InvitationDispatcherFactory.create(session, bootstrap),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[InstitutionService, Depends(get_institution_service)]
ProvisioningDep = Annotated[InstitutionProvisioningService, Depends(get_provisioning_service)]

router = APIRouter(
    prefix="/institutions",
    tags=["institutions"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("", response_model=list[InstitutionSummary])
def list_institutions(service: ServiceDep) -> list[InstitutionSummary]:
    return service.list_institutions()


@router.post("", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
def create_institution(
    request: InstitutionCreateRequest, service: ProvisioningDep, admin: SuperAdmin
) -> InstitutionResponse:
    return service.provision(InstitutionProvisioningCommand(**request.model_dump()), admin.id)


@router.get("/{institution_id}", response_model=InstitutionResponse)
def get_institution(institution_id: uuid.UUID, service: ServiceDep) -> InstitutionResponse:
    return service.get(institution_id)


@router.patch("/{institution_id}", response_model=InstitutionResponse)
def update_institution(
    institution_id: uuid.UUID,
    request: InstitutionUpdateRequest,
    service: ServiceDep,
    admin: SuperAdmin,
) -> InstitutionResponse:
    return service.update(institution_id, request, admin.id)


@router.post("/{institution_id}/deactivate", response_model=InstitutionResponse)
def deactivate_institution(
    institution_id: uuid.UUID, service: ServiceDep, admin: SuperAdmin
) -> InstitutionResponse:
    return service.deactivate(institution_id, admin.id)


@router.post("/{institution_id}/activate", response_model=InstitutionResponse)
def activate_institution(
    institution_id: uuid.UUID, service: ServiceDep, admin: SuperAdmin
) -> InstitutionResponse:
    return service.activate(institution_id, admin.id)


@router.post("/{institution_id}/manager-invitation", response_model=InstitutionResponse)
def resend_manager_invitation(
    institution_id: uuid.UUID, service: ProvisioningDep, admin: SuperAdmin
) -> InstitutionResponse:
    return service.resend_manager_invitation(institution_id, admin.id)
