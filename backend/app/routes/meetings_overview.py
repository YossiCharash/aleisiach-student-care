from fastapi import APIRouter, Depends

from backend.app.routes.meetings import ServiceDep
from backend.app.routes.security import CurrentUser, require_tenant
from backend.app.schema.service.meeting_overview_item import MeetingOverviewItem
from backend.app.service.students.student_access_policy import StudentAccessPolicy

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
    dependencies=[Depends(require_tenant)],
)


@router.get("/overview", response_model=list[MeetingOverviewItem])
def meetings_overview(service: ServiceDep, user: CurrentUser) -> list[MeetingOverviewItem]:
    return service.overview(StudentAccessPolicy.scope_for(user))
