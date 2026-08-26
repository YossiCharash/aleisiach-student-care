import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.sub_label import SubLabel
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_entry_request import MeetingEntryRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.meetings.meeting_service import MeetingService
from backend.app.service.program.program_service import ProgramService
from backend.app.service.students.student_access_guard import StudentAccessGuard

_ALL = StudentAccessScope(all_classes=True)
_AUTHOR = uuid.uuid4()


class _Bundle:
    def __init__(
        self,
        meetings: MeetingService,
        program: ProgramService,
        student_id: uuid.UUID,
        skill_a: uuid.UUID,
        skill_b: uuid.UUID,
        solution_b: uuid.UUID,
    ) -> None:
        self.meetings = meetings
        self.program = program
        self.student_id = student_id
        self.skill_a = skill_a
        self.skill_b = skill_b
        self.solution_b = solution_b


def _setup(session: Session) -> _Bundle:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    label = Label(name="עצמאות")
    session.add(label)
    session.flush()
    sub_label = SubLabel(label_id=label.id, name="היגיינה")
    session.add(sub_label)
    session.flush()
    skill_a = Skill(sub_label_id=sub_label.id, name="רחיצת ידיים")
    skill_b = Skill(sub_label_id=sub_label.id, name="צחצוח שיניים")
    session.add_all([skill_a, skill_b])
    session.flush()
    solution_b = Solution(skill_id=skill_b.id, text="תרגול יומי")
    session.add(solution_b)
    session.flush()
    guard = StudentAccessGuard(StudentRepository(session))
    meetings = MeetingService(MeetingRepository(session), guard, TaxonomyRepository(session))
    program = ProgramService(MeetingRepository(session), guard)
    return _Bundle(meetings, program, student.id, skill_a.id, skill_b.id, solution_b.id)


def _meeting(bundle: _Bundle, year: int, month: int, entries: list[MeetingEntryRequest]) -> None:
    request = MeetingCreateRequest(year=year, month=month, entries=entries)
    bundle.meetings.create(bundle.student_id, request, _ALL, _AUTHOR)


def test_latest_meeting_overrides_earlier_rating(db_session: Session) -> None:
    bundle = _setup(db_session)
    _meeting(
        bundle,
        2026,
        3,
        [
            MeetingEntryRequest(
                skill_id=bundle.skill_b,
                rating=MeetingRating.RED,
                solution_ids=[bundle.solution_b],
            )
        ],
    )
    _meeting(
        bundle,
        2026,
        8,
        [MeetingEntryRequest(skill_id=bundle.skill_b, rating=MeetingRating.GREEN)],
    )

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert [strength.skill_id for strength in program.strengths] == [bundle.skill_b]
    assert program.areas_to_strengthen == []


def test_accumulates_skills_and_exposes_solution_path(db_session: Session) -> None:
    bundle = _setup(db_session)
    _meeting(
        bundle,
        2026,
        3,
        [
            MeetingEntryRequest(
                skill_id=bundle.skill_b,
                rating=MeetingRating.YELLOW,
                solution_ids=[bundle.solution_b],
            )
        ],
    )
    _meeting(
        bundle,
        2026,
        8,
        [MeetingEntryRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN)],
    )

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert [strength.skill_id for strength in program.strengths] == [bundle.skill_a]
    assert len(program.areas_to_strengthen) == 1
    area = program.areas_to_strengthen[0]
    assert area.skill_id == bundle.skill_b
    assert area.rating == MeetingRating.YELLOW
    assert area.solutions == ["תרגול יומי"]


def test_single_meeting_splits_into_both_buckets(db_session: Session) -> None:
    bundle = _setup(db_session)
    _meeting(
        bundle,
        2026,
        8,
        [
            MeetingEntryRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN),
            MeetingEntryRequest(
                skill_id=bundle.skill_b,
                rating=MeetingRating.YELLOW,
                solution_ids=[bundle.solution_b],
            ),
        ],
    )

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert [strength.skill_id for strength in program.strengths] == [bundle.skill_a]
    assert [area.skill_id for area in program.areas_to_strengthen] == [bundle.skill_b]
    assert program.areas_to_strengthen[0].solutions == ["תרגול יומי"]


def test_no_meetings_yields_empty_program(db_session: Session) -> None:
    bundle = _setup(db_session)

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert program.strengths == []
    assert program.areas_to_strengthen == []


def test_student_outside_scope_is_hidden(db_session: Session) -> None:
    bundle = _setup(db_session)
    foreign = StudentAccessScope(all_classes=False, class_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        bundle.program.get_for_student(bundle.student_id, foreign)
