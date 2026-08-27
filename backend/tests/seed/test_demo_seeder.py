from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_entry_solution import MeetingEntrySolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.social_note import SocialNote
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.seed.demo_credentials import ALL_ACCOUNTS, DEMO_PASSWORD, INSTRUCTOR
from backend.app.seed.demo_seeder import DemoSeeder
from backend.app.utils.service.password_hasher import PasswordHasher


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def _seed(session: Session) -> DemoSeeder:
    seeder = DemoSeeder(session, PasswordHasher())
    seeder.run()
    return seeder


def test_run_creates_all_three_roles(db_session: Session) -> None:
    _seed(db_session)

    roles = set(db_session.scalars(select(User.role)).all())
    assert roles == {
        UserRole.MANAGER,
        UserRole.INSTRUCTOR,
        UserRole.PROFESSIONAL_TEACHER,
    }
    assert all(user.status == UserStatus.ACTIVE for user in db_session.scalars(select(User)).all())


def test_instructor_is_assigned_to_a_class(db_session: Session) -> None:
    _seed(db_session)

    instructor = db_session.scalars(select(User).where(User.email == INSTRUCTOR.email)).one()
    assert instructor.class_id is not None


def test_demo_passwords_verify(db_session: Session) -> None:
    _seed(db_session)
    hasher = PasswordHasher()

    for account in ALL_ACCOUNTS:
        user = db_session.scalars(select(User).where(User.email == account.email)).one()
        assert user.password_hash is not None
        assert hasher.verify(user.password_hash, DEMO_PASSWORD)


def test_seeds_classes_students_and_taxonomy(db_session: Session) -> None:
    _seed(db_session)

    assert _count(db_session, ClassEntity) == 2
    assert _count(db_session, Student) == 3
    assert _count(db_session, SubLabel) == 2
    assert _count(db_session, Skill) == 3
    assert _count(db_session, Solution) == 4


def test_seeds_meeting_with_rated_entries_and_solutions(db_session: Session) -> None:
    _seed(db_session)

    meeting = db_session.scalars(select(TeamMeeting)).one()
    entries = db_session.scalars(
        select(MeetingEntry).where(MeetingEntry.meeting_id == meeting.id)
    ).all()
    assert {entry.rating for entry in entries} == {
        MeetingRating.GREEN,
        MeetingRating.YELLOW,
        MeetingRating.RED,
    }
    assert _count(db_session, MeetingEntrySolution) == 2


def test_seeds_details_and_social_note(db_session: Session) -> None:
    _seed(db_session)

    assert _count(db_session, StudentDetails) == 1
    assert _count(db_session, SocialNote) == 1


def test_run_is_idempotent(db_session: Session) -> None:
    seeder = _seed(db_session)
    assert seeder.is_seeded()

    seeder.run()

    assert _count(db_session, User) == len(ALL_ACCOUNTS)
    assert _count(db_session, Student) == 3
    assert _count(db_session, TeamMeeting) == 1
