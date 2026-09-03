import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.student import Student
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.schema.service.meeting_overview_item import MeetingOverviewItem
from backend.app.schema.service.student_access_scope import StudentAccessScope


class MeetingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, meeting: TeamMeeting) -> TeamMeeting:
        self._session.add(meeting)
        self._session.flush()
        return meeting

    def get(self, meeting_id: uuid.UUID) -> TeamMeeting | None:
        return self._session.get(TeamMeeting, meeting_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[TeamMeeting]:
        statement = (
            select(TeamMeeting)
            .where(TeamMeeting.student_id == student_id)
            .order_by(
                TeamMeeting.year.desc(),
                TeamMeeting.month.desc(),
                TeamMeeting.created_at.desc(),
                TeamMeeting.id.desc(),
            )
            .options(selectinload(TeamMeeting.entries).selectinload(MeetingEntry.solutions))
        )
        return list(self._session.scalars(statement).all())

    def list_overview(self, scope: StudentAccessScope) -> list[MeetingOverviewItem]:
        institution_id = TenantBinding.require(self._session)
        statement = (
            select(
                TeamMeeting.id,
                TeamMeeting.student_id,
                TeamMeeting.year,
                TeamMeeting.month,
                Student.full_name,
            )
            .join(Student, Student.id == TeamMeeting.student_id)
            .where(
                TeamMeeting.institution_id == institution_id,
                Student.institution_id == institution_id,
                Student.is_archived.is_(False),
            )
            .order_by(TeamMeeting.year.desc(), TeamMeeting.month.desc(), Student.full_name)
        )
        if not scope.all_classes:
            statement = statement.where(Student.class_id == scope.class_id)
        rows = self._session.execute(statement).all()
        return [
            MeetingOverviewItem(
                meeting_id=row.id,
                student_id=row.student_id,
                student_name=row.full_name,
                year=row.year,
                month=row.month,
            )
            for row in rows
        ]
