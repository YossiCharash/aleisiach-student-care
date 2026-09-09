from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_foci_entry import MeetingFociEntry
from backend.app.models.client.meeting_plan_entry import MeetingPlanEntry
from backend.app.models.client.meeting_plan_solution import MeetingPlanSolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.social_note_entry import SocialNoteEntry
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.seed.demo_credentials import (
    ALL_ACCOUNTS,
    DEMO_INSTITUTION_CODE,
    DEMO_PASSWORD,
    INSTRUCTOR,
)
from backend.app.seed.demo_seeder import DemoSeeder
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.tests.support.tenant_filter_disabled import tenant_filter_disabled


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


def test_instructor_is_assigned_to_a_workshop(db_session: Session) -> None:
    _seed(db_session)

    instructor = db_session.scalars(select(User).where(User.email == INSTRUCTOR.email)).one()
    assert instructor.workshop_id is not None


def test_demo_passwords_verify(db_session: Session) -> None:
    _seed(db_session)
    hasher = PasswordHasher()

    for account in ALL_ACCOUNTS:
        user = db_session.scalars(select(User).where(User.email == account.email)).one()
        assert user.password_hash is not None
        assert hasher.verify(user.password_hash, DEMO_PASSWORD)


def test_seeds_workshops_students_and_taxonomy(db_session: Session) -> None:
    _seed(db_session)

    assert _count(db_session, Workshop) == 2
    assert _count(db_session, Student) == 3
    assert _count(db_session, Label) == 2
    assert _count(db_session, Skill) == 3
    assert _count(db_session, Solution) == 4


def test_seeds_meeting_snapshotting_foci_plan_and_summary(db_session: Session) -> None:
    _seed(db_session)

    meeting = db_session.scalars(select(TeamMeeting)).one()
    foci = db_session.scalars(
        select(MeetingFociEntry).where(MeetingFociEntry.meeting_id == meeting.id)
    ).all()
    assert {entry.rating for entry in foci} == {
        MeetingRating.GREEN,
        MeetingRating.YELLOW,
        MeetingRating.RED,
    }
    assert _count(db_session, MeetingPlanEntry) == 2
    assert _count(db_session, MeetingPlanSolution) == 2
    assert meeting.summary != ""
    assert meeting.meeting_date is not None


def test_seeds_details_and_social_note(db_session: Session) -> None:
    _seed(db_session)

    assert _count(db_session, StudentDetails) == 1
    assert _count(db_session, SocialNoteEntry) == 2


def test_seeded_details_deserialize_through_response_schemas(db_session: Session) -> None:
    _seed(db_session)

    details = db_session.scalars(select(StudentDetails)).one()
    contacts = [ContactInfo(**item) for item in [*details.emergency_contacts, *details.guardians]]

    assert all(contact.full_name for contact in contacts)
    assert details.idd_severity is not None
    assert all(isinstance(name, str) for name in details.additional_diagnoses)


def test_run_is_idempotent(db_session: Session) -> None:
    seeder = _seed(db_session)
    assert seeder.is_seeded()

    seeder.run()

    assert _count(db_session, User) == len(ALL_ACCOUNTS)
    assert _count(db_session, Student) == 3
    assert _count(db_session, TeamMeeting) == 1


def test_every_seeded_row_belongs_to_the_demo_institution(db_session: Session) -> None:
    _seed(db_session)

    with TenantBinding.platform(db_session):
        institution = db_session.scalars(
            select(Institution).where(Institution.code == DEMO_INSTITUTION_CODE)
        ).one()
        owners = {
            model.__name__: {row.institution_id for row in db_session.scalars(select(model)).all()}
            for model in (Workshop, Student, Label, Skill, Solution)
        }

    assert owners == {model: {institution.id} for model in owners}


def test_seeded_users_belong_to_the_demo_institution(db_session: Session) -> None:
    _seed(db_session)

    with TenantBinding.platform(db_session):
        institution = db_session.scalars(
            select(Institution).where(Institution.code == DEMO_INSTITUTION_CODE)
        ).one()
        owners = {user.institution_id for user in db_session.scalars(select(User)).all()}

    assert owners == {institution.id}


def test_seeding_states_the_institution_without_relying_on_the_orm_filter(
    db_session: Session,
) -> None:
    with tenant_filter_disabled():
        _seed(db_session)

    with TenantBinding.platform(db_session):
        institution = db_session.scalars(
            select(Institution).where(Institution.code == DEMO_INSTITUTION_CODE)
        ).one()
        classes = db_session.scalars(select(Workshop)).all()
        students = db_session.scalars(select(Student)).all()
        labels = db_session.scalars(select(Label)).all()
        users = db_session.scalars(select(User)).all()

    seeded = list(classes) + list(students) + list(labels) + list(users)
    assert seeded
    assert {row.institution_id for row in seeded} == {institution.id}
