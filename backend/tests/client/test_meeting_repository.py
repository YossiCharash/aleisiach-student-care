import uuid

from sqlalchemy.orm import Session

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.team_meeting import TeamMeeting


def _seed_student(session: Session) -> uuid.UUID:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    return student.id


def test_list_for_student_orders_newest_first(db_session: Session) -> None:
    student_id = _seed_student(db_session)
    repository = MeetingRepository(db_session)
    author_id = uuid.uuid4()
    repository.add(TeamMeeting(student_id=student_id, year=2026, month=3, author_id=author_id))
    repository.add(TeamMeeting(student_id=student_id, year=2026, month=8, author_id=author_id))
    repository.add(TeamMeeting(student_id=student_id, year=2025, month=12, author_id=author_id))

    months = [(m.year, m.month) for m in repository.list_for_student(student_id)]

    assert months == [(2026, 8), (2026, 3), (2025, 12)]


def test_list_for_student_excludes_other_students(db_session: Session) -> None:
    student_id = _seed_student(db_session)
    other_id = _seed_student(db_session)
    repository = MeetingRepository(db_session)
    repository.add(TeamMeeting(student_id=student_id, year=2026, month=8, author_id=uuid.uuid4()))
    repository.add(TeamMeeting(student_id=other_id, year=2026, month=8, author_id=uuid.uuid4()))

    meetings = repository.list_for_student(student_id)

    assert len(meetings) == 1
    assert meetings[0].student_id == student_id
