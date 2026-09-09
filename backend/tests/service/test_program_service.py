import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_skill_rating_error import InvalidSkillRatingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program import Program
from backend.app.models.client.skill import Skill
from backend.app.models.client.student import Student
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.focus_rating_request import FocusRatingRequest
from backend.app.schema.routes.program_upsert_request import ProgramUpsertRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.program.program_service import ProgramService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.taxonomy.skill_focus_resolver import SkillFocusResolver
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


class _Bundle:
    def __init__(
        self,
        program: ProgramService,
        student_id: uuid.UUID,
        author_id: uuid.UUID,
        skill_a: uuid.UUID,
        skill_b: uuid.UUID,
    ) -> None:
        self.program = program
        self.student_id = student_id
        self.author_id = author_id
        self.skill_a = skill_a
        self.skill_b = skill_b


def _setup(session: Session) -> _Bundle:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
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
    program = ProgramService(
        ProgramRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        SkillFocusResolver(TaxonomyRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )
    return _Bundle(program, student.id, seed_actor(session), skill_a.id, skill_b.id)


def _upsert(bundle: _Bundle, entries: list[FocusRatingRequest]) -> None:
    request = ProgramUpsertRequest(entries=entries)
    bundle.program.upsert(bundle.student_id, request, _ALL, bundle.author_id)


def test_no_program_yields_empty_response(db_session: Session) -> None:
    bundle = _setup(db_session)

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert program.exists is False
    assert program.entries == []
    assert program.strengths == []
    assert program.areas_to_strengthen == []


def test_upsert_splits_entries_into_strengths_and_areas(db_session: Session) -> None:
    bundle = _setup(db_session)
    _upsert(
        bundle,
        [
            FocusRatingRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN),
            FocusRatingRequest(skill_id=bundle.skill_b, rating=MeetingRating.YELLOW),
        ],
    )

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert program.exists is True
    assert [strength.skill_id for strength in program.strengths] == [bundle.skill_a]
    assert [area.skill_id for area in program.areas_to_strengthen] == [bundle.skill_b]
    assert program.areas_to_strengthen[0].rating == MeetingRating.YELLOW
    assert len(program.entries) == 2


def test_upsert_replaces_previous_entries(db_session: Session) -> None:
    bundle = _setup(db_session)
    _upsert(bundle, [FocusRatingRequest(skill_id=bundle.skill_b, rating=MeetingRating.RED)])
    _upsert(bundle, [FocusRatingRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN)])

    program = bundle.program.get_for_student(bundle.student_id, _ALL)

    assert [entry.skill_id for entry in program.entries] == [bundle.skill_a]
    assert [strength.skill_id for strength in program.strengths] == [bundle.skill_a]
    assert program.areas_to_strengthen == []


def test_create_then_update_are_audited(db_session: Session) -> None:
    bundle = _setup(db_session)
    _upsert(bundle, [FocusRatingRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN)])
    _upsert(bundle, [FocusRatingRequest(skill_id=bundle.skill_b, rating=MeetingRating.GREEN)])

    logs = db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)).all()
    actions = [log.action for log in logs]
    assert actions == [AuditAction.CREATE, AuditAction.UPDATE]
    assert all(log.entity_type == "program" for log in logs)


def test_duplicate_skill_is_rejected(db_session: Session) -> None:
    bundle = _setup(db_session)

    with pytest.raises(InvalidSkillRatingError):
        _upsert(
            bundle,
            [
                FocusRatingRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN),
                FocusRatingRequest(skill_id=bundle.skill_a, rating=MeetingRating.RED),
            ],
        )


def test_unknown_skill_is_rejected(db_session: Session) -> None:
    bundle = _setup(db_session)

    with pytest.raises(NotFoundError):
        _upsert(bundle, [FocusRatingRequest(skill_id=uuid.uuid4(), rating=MeetingRating.GREEN)])


def test_update_keeps_original_creator(db_session: Session) -> None:
    bundle = _setup(db_session)
    editor = seed_actor(db_session, "editor")
    _upsert(bundle, [FocusRatingRequest(skill_id=bundle.skill_a, rating=MeetingRating.GREEN)])
    request = ProgramUpsertRequest(
        entries=[FocusRatingRequest(skill_id=bundle.skill_b, rating=MeetingRating.GREEN)]
    )
    bundle.program.upsert(bundle.student_id, request, _ALL, editor)

    stored = db_session.scalars(
        select(Program).where(Program.student_id == bundle.student_id)
    ).one()
    assert stored.author_id == bundle.author_id


def test_student_outside_scope_is_hidden(db_session: Session) -> None:
    bundle = _setup(db_session)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        bundle.program.get_for_student(bundle.student_id, foreign)
