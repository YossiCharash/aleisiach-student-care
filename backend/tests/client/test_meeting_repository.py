from sqlalchemy.orm import Session

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.models.client.team_meeting import TeamMeeting
from backend.tests.support.seeding import seed_actor, seed_student


def test_list_for_student_orders_newest_first(db_session: Session) -> None:
    student_id = seed_student(db_session)
    repository = MeetingRepository(db_session)
    author_id = seed_actor(db_session)
    repository.add(TeamMeeting(student_id=student_id, year=2026, month=3, author_id=author_id))
    repository.add(TeamMeeting(student_id=student_id, year=2026, month=8, author_id=author_id))
    repository.add(TeamMeeting(student_id=student_id, year=2025, month=12, author_id=author_id))

    months = [(m.year, m.month) for m in repository.list_for_student(student_id)]

    assert months == [(2026, 8), (2026, 3), (2025, 12)]


def test_list_for_student_excludes_other_students(db_session: Session) -> None:
    student_id = seed_student(db_session)
    other_id = seed_student(db_session, "Noa")
    author_id = seed_actor(db_session)
    repository = MeetingRepository(db_session)
    repository.add(TeamMeeting(student_id=student_id, year=2026, month=8, author_id=author_id))
    repository.add(TeamMeeting(student_id=other_id, year=2026, month=8, author_id=author_id))

    meetings = repository.list_for_student(student_id)

    assert len(meetings) == 1
    assert meetings[0].student_id == student_id
