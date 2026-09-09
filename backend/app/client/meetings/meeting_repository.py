import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.client.meeting_plan_entry import MeetingPlanEntry
from backend.app.models.client.team_meeting import TeamMeeting


class MeetingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, meeting: TeamMeeting) -> TeamMeeting:
        self._session.add(meeting)
        self._session.flush()
        return meeting

    def flush(self) -> None:
        self._session.flush()

    def get(self, meeting_id: uuid.UUID) -> TeamMeeting | None:
        statement = (
            select(TeamMeeting)
            .where(TeamMeeting.id == meeting_id)
            .options(
                selectinload(TeamMeeting.foci_entries),
                selectinload(TeamMeeting.plan_entries).selectinload(MeetingPlanEntry.solutions),
            )
        )
        return self._session.scalars(statement).one_or_none()

    def list_for_student(self, student_id: uuid.UUID) -> list[TeamMeeting]:
        statement = (
            select(TeamMeeting)
            .where(TeamMeeting.student_id == student_id)
            .order_by(
                TeamMeeting.meeting_date.desc(),
                TeamMeeting.created_at.desc(),
                TeamMeeting.id.desc(),
            )
            .options(
                selectinload(TeamMeeting.foci_entries),
                selectinload(TeamMeeting.plan_entries).selectinload(MeetingPlanEntry.solutions),
            )
        )
        return list(self._session.scalars(statement).all())
