import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_meeting_error import InvalidMeetingError
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

_ALL = StudentAccessScope(all_classes=True)


class _Fixture:
    def __init__(
        self,
        service: MeetingService,
        student_id: uuid.UUID,
        skill_id: uuid.UUID,
        other_skill_id: uuid.UUID,
        solution_id: uuid.UUID,
        other_solution_id: uuid.UUID,
    ) -> None:
        self.service = service
        self.student_id = student_id
        self.skill_id = skill_id
        self.other_skill_id = other_skill_id
        self.solution_id = solution_id
        self.other_solution_id = other_solution_id


def _setup(session: Session) -> _Fixture:
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
    skill = Skill(sub_label_id=sub_label.id, name="רחיצת ידיים")
    other_skill = Skill(sub_label_id=sub_label.id, name="צחצוח שיניים")
    session.add_all([skill, other_skill])
    session.flush()
    solution = Solution(skill_id=skill.id, text="תרגול יומי")
    other_solution = Solution(skill_id=other_skill.id, text="פתרון אחר")
    session.add_all([solution, other_solution])
    session.flush()
    service = MeetingService(
        MeetingRepository(session), StudentRepository(session), TaxonomyRepository(session)
    )
    return _Fixture(service, student.id, skill.id, other_skill.id, solution.id, other_solution.id)


def test_create_captures_snapshots(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[
            MeetingEntryRequest(
                skill_id=fx.skill_id,
                rating=MeetingRating.YELLOW,
                solution_ids=[fx.solution_id],
            )
        ],
    )

    meeting = fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())

    assert meeting.entries[0].skill_name_snapshot == "רחיצת ידיים"
    assert meeting.entries[0].solutions[0].solution_text_snapshot == "תרגול יומי"


def test_yellow_without_solution_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[MeetingEntryRequest(skill_id=fx.skill_id, rating=MeetingRating.RED)],
    )

    with pytest.raises(InvalidMeetingError):
        fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())


def test_green_with_solution_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[
            MeetingEntryRequest(
                skill_id=fx.skill_id,
                rating=MeetingRating.GREEN,
                solution_ids=[fx.solution_id],
            )
        ],
    )

    with pytest.raises(InvalidMeetingError):
        fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())


def test_solution_from_another_skill_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[
            MeetingEntryRequest(
                skill_id=fx.skill_id,
                rating=MeetingRating.YELLOW,
                solution_ids=[fx.other_solution_id],
            )
        ],
    )

    with pytest.raises(InvalidMeetingError):
        fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())


def test_unknown_skill_is_not_found(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[MeetingEntryRequest(skill_id=uuid.uuid4(), rating=MeetingRating.GREEN)],
    )

    with pytest.raises(NotFoundError):
        fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())


def test_student_outside_scope_is_hidden(db_session: Session) -> None:
    fx = _setup(db_session)
    foreign_scope = StudentAccessScope(all_classes=False, class_id=uuid.uuid4())
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[MeetingEntryRequest(skill_id=fx.skill_id, rating=MeetingRating.GREEN)],
    )

    with pytest.raises(NotFoundError):
        fx.service.create(fx.student_id, request, foreign_scope, uuid.uuid4())


def test_duplicate_skill_in_meeting_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[
            MeetingEntryRequest(skill_id=fx.skill_id, rating=MeetingRating.GREEN),
            MeetingEntryRequest(
                skill_id=fx.skill_id,
                rating=MeetingRating.RED,
                solution_ids=[fx.solution_id],
            ),
        ],
    )

    with pytest.raises(InvalidMeetingError):
        fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())


def test_duplicate_solution_in_entry_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[
            MeetingEntryRequest(
                skill_id=fx.skill_id,
                rating=MeetingRating.YELLOW,
                solution_ids=[fx.solution_id, fx.solution_id],
            )
        ],
    )

    with pytest.raises(InvalidMeetingError):
        fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())


def test_entries_are_persisted_in_request_order(db_session: Session) -> None:
    fx = _setup(db_session)
    request = MeetingCreateRequest(
        year=2026,
        month=8,
        entries=[
            MeetingEntryRequest(skill_id=fx.other_skill_id, rating=MeetingRating.GREEN),
            MeetingEntryRequest(skill_id=fx.skill_id, rating=MeetingRating.GREEN),
        ],
    )
    fx.service.create(fx.student_id, request, _ALL, uuid.uuid4())

    reloaded = fx.service.list_for_student(fx.student_id, _ALL)[0]

    assert [entry.skill_name_snapshot for entry in reloaded.entries] == [
        "צחצוח שיניים",
        "רחיצת ידיים",
    ]
