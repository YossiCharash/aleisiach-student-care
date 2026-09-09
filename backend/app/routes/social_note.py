import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.routes.pdf import BrandDep, RendererDep
from backend.app.routes.security import Manager, ManagerOrInstructor, Tenant, require_tenant
from backend.app.schema.routes.social_note_create_request import SocialNoteCreateRequest
from backend.app.schema.routes.social_note_entry_response import SocialNoteEntryResponse
from backend.app.schema.routes.social_note_report_response import SocialNoteReportResponse
from backend.app.schema.routes.social_note_update_request import SocialNoteUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.notes.social_note_document import SocialNoteDocument
from backend.app.service.notes.social_note_service import SocialNoteService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.service.clock import Clock


def get_social_note_service(
    session: Annotated[Session, Depends(get_session)],
) -> SocialNoteService:
    return SocialNoteService(
        SocialNoteRepository(session),
        UserRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
        Clock(),
    )


ServiceDep = Annotated[SocialNoteService, Depends(get_social_note_service)]

router = APIRouter(
    prefix="/students/{student_id}/social-note",
    tags=["social-note"],
    dependencies=[Depends(require_tenant)],
)


@router.get("", response_model=SocialNoteReportResponse)
def list_social_notes(
    student_id: uuid.UUID, service: ServiceDep, reader: ManagerOrInstructor
) -> SocialNoteReportResponse:
    return service.report(student_id, StudentAccessPolicy.scope_for(reader))


@router.post("", response_model=SocialNoteEntryResponse, status_code=status.HTTP_201_CREATED)
def create_social_note(
    student_id: uuid.UUID,
    request: SocialNoteCreateRequest,
    service: ServiceDep,
    manager: Manager,
) -> SocialNoteEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.create(student_id, request, scope, manager.id)


@router.patch("/{entry_id}", response_model=SocialNoteEntryResponse)
def update_social_note(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    request: SocialNoteUpdateRequest,
    service: ServiceDep,
    manager: Manager,
) -> SocialNoteEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.update(student_id, entry_id, request, scope, manager.id)


@router.post("/{entry_id}/archive", response_model=SocialNoteEntryResponse)
def archive_social_note(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    service: ServiceDep,
    manager: Manager,
) -> SocialNoteEntryResponse:
    scope = StudentAccessPolicy.scope_for(manager)
    return service.archive(student_id, entry_id, scope, manager.id)


@router.get("/pdf")
def get_social_notes_pdf(
    student_id: uuid.UUID,
    service: ServiceDep,
    reader: ManagerOrInstructor,
    renderer: RendererDep,
    brand: BrandDep,
    tenant: Tenant,
) -> Response:
    report = service.report(student_id, StudentAccessPolicy.scope_for(reader))
    html = SocialNoteDocument(brand).combined_html(report, tenant.institution_name)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="social-notes-{student_id}.pdf"'},
    )


@router.get("/{entry_id}/pdf")
def get_social_note_pdf(
    student_id: uuid.UUID,
    entry_id: uuid.UUID,
    service: ServiceDep,
    reader: ManagerOrInstructor,
    renderer: RendererDep,
    brand: BrandDep,
    tenant: Tenant,
) -> Response:
    report = service.entry_report(student_id, entry_id, StudentAccessPolicy.scope_for(reader))
    html = SocialNoteDocument(brand).single_html(report, tenant.institution_name)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="social-note-{entry_id}.pdf"'},
    )
