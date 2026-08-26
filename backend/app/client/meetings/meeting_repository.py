import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.team_meeting import TeamMeeting


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
            )
        )
        return list(self._session.scalars(statement).all())
