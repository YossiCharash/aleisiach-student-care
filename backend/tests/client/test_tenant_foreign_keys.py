import sqlite3
import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.base import Base
from backend.app.models.client.extra_section_type import ExtraSectionType
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
from backend.app.models.client.student_extra_section import StudentExtraSection
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.models.client.workshop import Workshop

HOME = uuid.UUID("22222222-2222-2222-2222-222222222222")
AWAY = uuid.UUID("33333333-3333-3333-3333-333333333333")


class Tenant:
    def __init__(self, session: Session, institution_id: uuid.UUID, code: str) -> None:
        self._session = session
        self.institution_id = institution_id
        workshop = Workshop(name=f"class-{code}", institution_id=institution_id)
        session.add(workshop)
        session.flush()
        self.student = Student(
            full_name=f"student-{code}",
            workshop_id=workshop.id,
            institution_id=institution_id,
        )
        label = Label(name=f"label-{code}", order=0, institution_id=institution_id)
        self.section_type = ExtraSectionType(
            name=f"section-{code}", order=0, institution_id=institution_id
        )
        self.author = User(
            full_name=f"author-{code}",
            email=f"author-{code}@example.com",
            username=f"author-{code}",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            institution_id=institution_id,
        )
        session.add_all([self.student, label, self.section_type, self.author])
        session.flush()
        self.skill = Skill(
            name=f"skill-{code}", order=0, label_id=label.id, institution_id=institution_id
        )
        session.add(self.skill)
        session.flush()
        self.solution = Solution(
            text=f"solution-{code}",
            skill_id=self.skill.id,
            rating=MeetingRating.YELLOW,
            institution_id=institution_id,
        )
        session.add(self.solution)
        session.flush()

    def meeting(self) -> TeamMeeting:
        meeting = TeamMeeting(
            student_id=self.student.id,
            meeting_date=date(2026, 6, 1),
            summary="",
            author_id=self.author.id,
            institution_id=self.institution_id,
        )
        self._session.add(meeting)
        self._session.flush()
        return meeting

    def plan_entry(self, meeting: TeamMeeting) -> MeetingPlanEntry:
        entry = MeetingPlanEntry(
            meeting_id=meeting.id,
            skill_id=self.skill.id,
            skill_name_snapshot=self.skill.name,
            rating=MeetingRating.GREEN,
            position=0,
            institution_id=self.institution_id,
        )
        self._session.add(entry)
        self._session.flush()
        return entry


def _enforce_sqlite_foreign_keys(connection: object, _: object) -> None:
    if isinstance(connection, sqlite3.Connection):
        connection.execute("PRAGMA foreign_keys=ON")


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _enforce_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    opened = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    opened.add_all(
        [
            Institution(id=HOME, name="home", code="home", is_active=True),
            Institution(id=AWAY, name="away", code="away", is_active=True),
        ]
    )
    opened.flush()
    TenantBinding.deny(opened)
    try:
        yield opened
    finally:
        opened.close()
        engine.dispose()


@pytest.fixture
def home(session: Session) -> Tenant:
    return Tenant(session, HOME, "home")


@pytest.fixture
def away(session: Session) -> Tenant:
    return Tenant(session, AWAY, "away")


def test_the_pragma_is_active(session: Session, home: Tenant) -> None:
    session.add(
        TeamMeeting(
            student_id=uuid.uuid4(),
            meeting_date=date(2026, 6, 1),
            summary="",
            author_id=home.author.id,
            institution_id=HOME,
        )
    )
    with pytest.raises(IntegrityError):
        session.flush()


def test_student_details_cannot_claim_a_foreign_student(
    session: Session, home: Tenant, away: Tenant
) -> None:
    session.add(StudentDetails(student_id=away.student.id, institution_id=HOME))

    with pytest.raises(IntegrityError):
        session.flush()


def test_social_note_cannot_claim_a_foreign_student(
    session: Session, home: Tenant, away: Tenant
) -> None:
    session.add(
        SocialNoteEntry(
            student_id=away.student.id,
            note_date=date(2026, 9, 9),
            content="נחטף",
            author_id=home.author.id,
            institution_id=HOME,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_meeting_cannot_hang_off_a_foreign_student(
    session: Session, home: Tenant, away: Tenant
) -> None:
    session.add(
        TeamMeeting(
            student_id=away.student.id,
            meeting_date=date(2026, 6, 1),
            summary="",
            author_id=home.author.id,
            institution_id=HOME,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_foci_entry_cannot_reference_a_foreign_skill(
    session: Session, home: Tenant, away: Tenant
) -> None:
    meeting = home.meeting()
    session.add(
        MeetingFociEntry(
            meeting_id=meeting.id,
            skill_id=away.skill.id,
            skill_name_snapshot="נחטף",
            rating=MeetingRating.GREEN,
            position=0,
            institution_id=HOME,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_plan_entry_cannot_hang_off_a_foreign_meeting(
    session: Session, home: Tenant, away: Tenant
) -> None:
    foreign_meeting = away.meeting()
    session.add(
        MeetingPlanEntry(
            meeting_id=foreign_meeting.id,
            skill_id=home.skill.id,
            skill_name_snapshot="נחטף",
            rating=MeetingRating.GREEN,
            position=0,
            institution_id=HOME,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_plan_solution_cannot_reference_a_foreign_solution(
    session: Session, home: Tenant, away: Tenant
) -> None:
    entry = home.plan_entry(home.meeting())
    session.add(
        MeetingPlanSolution(
            plan_entry_id=entry.id,
            solution_id=away.solution.id,
            solution_text_snapshot="נחטף",
            position=0,
            institution_id=HOME,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_extra_section_cannot_reference_a_foreign_section_type(
    session: Session, home: Tenant, away: Tenant
) -> None:
    session.add(
        StudentExtraSection(
            student_id=home.student.id,
            section_type_id=away.section_type.id,
            content="נחטף",
            institution_id=HOME,
        )
    )

    with pytest.raises(IntegrityError):
        session.flush()


def test_a_meeting_within_one_institution_is_accepted(session: Session, home: Tenant) -> None:
    entry = home.plan_entry(home.meeting())
    session.add(
        MeetingPlanSolution(
            plan_entry_id=entry.id,
            solution_id=home.solution.id,
            solution_text_snapshot=home.solution.text,
            position=0,
            institution_id=HOME,
        )
    )

    session.flush()
