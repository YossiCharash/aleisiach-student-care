import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.database.provider import get_session
from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.routes.security import ContentWriter, CurrentUser
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.meetings.meeting_service import MeetingService
from backend.app.service.meetings.meeting_summary_document import MeetingSummaryDocument
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy


def get_pdf_renderer(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> PdfRenderer:
    return bootstrap.pdf_renderer


RendererDep = Annotated[PdfRenderer, Depends(get_pdf_renderer)]


def get_meeting_service(
    session: Annotated[Session, Depends(get_session)],
) -> MeetingService:
    return MeetingService(
        MeetingRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        TaxonomyRepository(session),
        AuditLogger(AuditLogRepository(session)),
    )


ServiceDep = Annotated[MeetingService, Depends(get_meeting_service)]

router = APIRouter(prefix="/students/{student_id}/meetings", tags=["meetings"])


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    student_id: uuid.UUID,
    request: MeetingCreateRequest,
    service: ServiceDep,
    writer: ContentWriter,
) -> MeetingResponse:
    scope = StudentAccessPolicy.scope_for(writer)
    return service.create(student_id, request, scope, writer.id)


@router.get("", response_model=list[MeetingResponse])
def list_meetings(
    student_id: uuid.UUID, service: ServiceDep, user: CurrentUser
) -> list[MeetingResponse]:
    return service.list_for_student(student_id, StudentAccessPolicy.scope_for(user))


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    student_id: uuid.UUID,
    meeting_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
) -> MeetingResponse:
    return service.get(student_id, meeting_id, StudentAccessPolicy.scope_for(user))


@router.get("/{meeting_id}/pdf")
def get_meeting_pdf(
    student_id: uuid.UUID,
    meeting_id: uuid.UUID,
    service: ServiceDep,
    user: CurrentUser,
    renderer: RendererDep,
) -> Response:
    meeting = service.get(student_id, meeting_id, StudentAccessPolicy.scope_for(user))
    html = MeetingSummaryDocument().to_html(meeting)
    pdf = renderer.render(html)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="meeting-{meeting_id}.pdf"'},
    )
