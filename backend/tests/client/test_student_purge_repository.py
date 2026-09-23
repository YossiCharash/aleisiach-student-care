import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.students.student_purge_repository import StudentPurgeRepository
from backend.app.models.base import Base
from backend.app.models.client.extra_section_type import ExtraSectionType
from backend.app.models.client.functional_report import FunctionalReport
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_foci_entry import MeetingFociEntry
from backend.app.models.client.meeting_plan_entry import MeetingPlanEntry
from backend.app.models.client.meeting_plan_solution import MeetingPlanSolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program import Program
from backend.app.models.client.program_entry import ProgramEntry
from backend.app.models.client.program_plan import ProgramPlan
from backend.app.models.client.program_plan_entry import ProgramPlanEntry
from backend.app.models.client.program_plan_solution import ProgramPlanSolution
from backend.app.models.client.reception_report import ReceptionReport
from backend.app.models.client.skill import Skill
from backend.app.models.client.social_note_entry import SocialNoteEntry
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.student_extra_section import StudentExtraSection
from backend.app.models.client.supported_employment import SupportedEmployment
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.workshop import Workshop
from backend.app.utils.service.password_hasher import PasswordHasher

_INSTITUTION_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
_RATING = next(iter(MeetingRating))


def _seed_full_subtree(session: Session) -> uuid.UUID:
    workshop = Workshop(name=f"Aleph-{uuid.uuid4().hex[:8]}", institution_id=_INSTITUTION_ID)
    session.add(workshop)
    session.flush()
    tag = uuid.uuid4().hex[:8]
    author = User(
        full_name="Boss",
        email=f"boss-{tag}@example.com",
        username=f"boss-{tag}",
        password_hash=PasswordHasher().hash("password123"),
        role=UserRole.MANAGER,
        institution_id=_INSTITUTION_ID,
    )
    session.add(author)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id, institution_id=_INSTITUTION_ID)
    session.add(student)
    session.flush()

    label = Label(name=f"Label-{tag}", institution_id=_INSTITUTION_ID)
    session.add(label)
    session.flush()
    skill = Skill(name=f"Skill-{tag}", institution_id=_INSTITUTION_ID, label_id=label.id)
    session.add(skill)
    session.flush()
    solution = Solution(
        skill_id=skill.id, institution_id=_INSTITUTION_ID, text="Do", rating=_RATING
    )
    session.add(solution)
    session.flush()
    skill_id = skill.id
    solution_id = solution.id

    session.add(StudentDetails(student_id=student.id, institution_id=_INSTITUTION_ID))

    meeting = TeamMeeting(
        student_id=student.id, institution_id=_INSTITUTION_ID, meeting_date=date.today()
    )
    meeting.author_id = author.id
    session.add(meeting)
    session.flush()
    session.add(
        MeetingFociEntry(
            meeting_id=meeting.id,
            institution_id=_INSTITUTION_ID,
            skill_id=skill_id,
            skill_name_snapshot="Skill",
            rating=_RATING,
            position=0,
        )
    )
    plan_entry = MeetingPlanEntry(
        meeting_id=meeting.id,
        institution_id=_INSTITUTION_ID,
        skill_id=skill_id,
        skill_name_snapshot="Skill",
        rating=_RATING,
        position=0,
    )
    session.add(plan_entry)
    session.flush()
    session.add(
        MeetingPlanSolution(
            plan_entry_id=plan_entry.id,
            institution_id=_INSTITUTION_ID,
            solution_id=solution_id,
            solution_text_snapshot="Do",
            position=0,
        )
    )

    program = Program(student_id=student.id, institution_id=_INSTITUTION_ID, author_id=author.id)
    session.add(program)
    session.flush()
    session.add(
        ProgramEntry(
            program_id=program.id,
            institution_id=_INSTITUTION_ID,
            skill_id=skill_id,
            skill_name_snapshot="Skill",
            rating=_RATING,
            position=0,
        )
    )

    plan = ProgramPlan(student_id=student.id, institution_id=_INSTITUTION_ID, author_id=author.id)
    session.add(plan)
    session.flush()
    program_plan_entry = ProgramPlanEntry(
        plan_id=plan.id,
        institution_id=_INSTITUTION_ID,
        skill_id=skill_id,
        skill_name_snapshot="Skill",
        rating=_RATING,
        position=0,
    )
    session.add(program_plan_entry)
    session.flush()
    session.add(
        ProgramPlanSolution(
            plan_entry_id=program_plan_entry.id,
            institution_id=_INSTITUTION_ID,
            solution_id=solution_id,
            solution_text_snapshot="Do",
            position=0,
        )
    )

    session.add(
        SocialNoteEntry(
            student_id=student.id,
            institution_id=_INSTITUTION_ID,
            note_date=date.today(),
            author_id=author.id,
        )
    )
    now = datetime.now(UTC)
    session.add(
        FunctionalReport(
            student_id=student.id,
            institution_id=_INSTITUTION_ID,
            updated_by=author.id,
            updated_at=now,
        )
    )
    session.add(
        ReceptionReport(
            student_id=student.id,
            institution_id=_INSTITUTION_ID,
            updated_by=author.id,
            updated_at=now,
        )
    )
    session.add(
        SupportedEmployment(
            student_id=student.id,
            institution_id=_INSTITUTION_ID,
            updated_by=author.id,
            updated_at=now,
        )
    )
    section_type = ExtraSectionType(name=f"Heading-{tag}", institution_id=_INSTITUTION_ID)
    session.add(section_type)
    session.flush()
    session.add(
        StudentExtraSection(
            student_id=student.id, institution_id=_INSTITUTION_ID, section_type_id=section_type.id
        )
    )
    session.flush()
    return student.id


def _row_count(session: Session, model: type[Base]) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_purge_removes_the_whole_student_subtree(db_session: Session) -> None:
    student_id = _seed_full_subtree(db_session)

    StudentPurgeRepository(db_session).purge(student_id)

    assert db_session.get(Student, student_id) is None
    for model in (
        StudentDetails,
        TeamMeeting,
        MeetingFociEntry,
        MeetingPlanEntry,
        MeetingPlanSolution,
        Program,
        ProgramEntry,
        ProgramPlan,
        ProgramPlanEntry,
        ProgramPlanSolution,
        SocialNoteEntry,
        FunctionalReport,
        ReceptionReport,
        SupportedEmployment,
        StudentExtraSection,
    ):
        assert _row_count(db_session, model) == 0


def test_purge_keeps_other_students(db_session: Session) -> None:
    kept = _seed_full_subtree(db_session)
    other = _seed_full_subtree(db_session)

    StudentPurgeRepository(db_session).purge(other)

    assert db_session.get(Student, kept) is not None
    assert db_session.get(Student, other) is None
    assert _row_count(db_session, TeamMeeting) == 1
