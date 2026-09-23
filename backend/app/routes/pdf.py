import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.client.database.provider import get_session
from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.client.students.student_repository import StudentRepository
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.configuration.provider import get_bootstrap
from backend.app.routes.security import CurrentUser, Tenant
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.students.student_access_policy import StudentAccessPolicy
from backend.app.utils.service.clock import Clock


def get_pdf_renderer(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> PdfRenderer:
    return bootstrap.pdf_renderer


RendererDep = Annotated[PdfRenderer, Depends(get_pdf_renderer)]


def get_brand_settings(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> BrandSettings:
    return bootstrap.settings.brand


BrandDep = Annotated[BrandSettings, Depends(get_brand_settings)]


def build_issue_context(
    student_id: uuid.UUID,
    user: CurrentUser,
    tenant: Tenant,
    session: Annotated[Session, Depends(get_session)],
) -> IssueContext:
    scope = StudentAccessPolicy.scope_for(user)
    student = StudentAccessGuard(StudentRepository(session)).require(student_id, scope)
    return IssueContext(
        institution_name=tenant.institution_name,
        student_name=student.full_name,
        issued_by=user.full_name,
        issue_date=Clock().today(),
    )


Issue = Annotated[IssueContext, Depends(build_issue_context)]
