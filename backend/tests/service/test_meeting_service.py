import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.program.program_plan_repository import ProgramPlanRepository
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program import Program
from backend.app.models.client.program_entry import ProgramEntry
from backend.app.models.client.program_plan import ProgramPlan
from backend.app.models.client.program_plan_entry import ProgramPlanEntry
from backend.app.models.client.program_plan_solution import ProgramPlanSolution
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_update_request import MeetingUpdateRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.meetings.meeting_service import MeetingService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


class _Fixture:
    def __init__(
        self,
        service: MeetingService,
        session: Session,
        student_id: uuid.UUID,
        bare_student_id: uuid.UUID,
        author_id: uuid.UUID,
        program: Program,
    ) -> None:
        self.service = service
        self.session = session
        self.student_id = student_id
        self.bare_student_id = bare_student_id
        self.author_id = author_id
        self.program = program


def _setup(session: Session) -> _Fixture:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    bare_student = Student(full_name="Roni", workshop_id=workshop.id)
    session.add_all([student, bare_student])
    label = Label(name="עצמאות")
    session.add(label)
    session.flush()
    sub_label = SubLabel(label_id=label.id, name="היגיינה")
    session.add(sub_label)
    session.flush()
    strength = Skill(sub_label_id=sub_label.id, name="הבעה")
    area = Skill(sub_label_id=sub_label.id, name="רחיצת ידיים")
    session.add_all([strength, area])
    session.flush()
    solution = Solution(skill_id=area.id, text="תרגול יומי", rating=MeetingRating.YELLOW)
    session.add(solution)
    session.flush()
    author_id = seed_actor(session)

    program = Program(student_id=student.id, author_id=author_id)
    program.entries = [
        ProgramEntry(
            skill_id=strength.id,
            skill_name_snapshot=strength.name,
            rating=MeetingRating.GREEN,
            position=0,
        ),
        ProgramEntry(
            skill_id=area.id,
            skill_name_snapshot=area.name,
            rating=MeetingRating.YELLOW,
            position=1,
        ),
    ]
    session.add(program)

    plan = ProgramPlan(student_id=student.id, author_id=author_id)
    plan_entry = ProgramPlanEntry(
        skill_id=area.id,
        skill_name_snapshot=area.name,
        rating=MeetingRating.YELLOW,
        position=0,
    )
    plan_entry.solutions = [
        ProgramPlanSolution(
            solution_id=solution.id,
            solution_text_snapshot=solution.text,
            position=0,
        )
    ]
    plan.entries = [plan_entry]
    session.add(plan)
    session.flush()

    service = MeetingService(
        MeetingRepository(session),
        ProgramRepository(session),
        ProgramPlanRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )
    return _Fixture(service, session, student.id, bare_student.id, author_id, program)


def _request(summary: str = "סיכום") -> MeetingCreateRequest:
    return MeetingCreateRequest(meeting_date=date(2026, 8, 15), summary=summary)


def test_create_snapshots_current_foci_and_latest_plan(db_session: Session) -> None:
    fx = _setup(db_session)

    meeting = fx.service.create(fx.student_id, _request(), _ALL, fx.author_id)

    assert meeting.meeting_date == date(2026, 8, 15)
    assert meeting.summary == "סיכום"
    assert [strength.skill_name for strength in meeting.strengths] == ["הבעה"]
    assert [area.skill_name for area in meeting.areas_to_strengthen] == ["רחיצת ידיים"]
    assert meeting.plan_entries[0].skill_name_snapshot == "רחיצת ידיים"
    assert meeting.plan_entries[0].solutions[0].solution_text_snapshot == "תרגול יומי"


def test_create_without_foci_or_plan_is_allowed(db_session: Session) -> None:
    fx = _setup(db_session)

    meeting = fx.service.create(fx.bare_student_id, _request("רק סיכום"), _ALL, fx.author_id)

    assert meeting.strengths == []
    assert meeting.areas_to_strengthen == []
    assert meeting.plan_entries == []
    assert meeting.summary == "רק סיכום"


def test_snapshot_is_frozen_when_foci_change_later(db_session: Session) -> None:
    fx = _setup(db_session)
    meeting = fx.service.create(fx.student_id, _request(), _ALL, fx.author_id)

    fx.program.entries = []
    fx.session.flush()

    reloaded = fx.service.get(fx.student_id, meeting.id, _ALL)
    assert [strength.skill_name for strength in reloaded.strengths] == ["הבעה"]
    assert [area.skill_name for area in reloaded.areas_to_strengthen] == ["רחיצת ידיים"]


def test_create_is_audited(db_session: Session) -> None:
    fx = _setup(db_session)

    fx.service.create(fx.student_id, _request(), _ALL, fx.author_id)

    log = db_session.scalars(select(AuditLog)).one()
    assert log.action == AuditAction.CREATE
    assert log.entity_type == "team_meeting"
    assert log.actor_id == fx.author_id


def test_update_summary_changes_text_without_touching_the_snapshot(db_session: Session) -> None:
    fx = _setup(db_session)
    meeting = fx.service.create(fx.student_id, _request("ראשוני"), _ALL, fx.author_id)

    updated = fx.service.update_summary(
        fx.student_id, meeting.id, MeetingUpdateRequest(summary="מעודכן"), _ALL, fx.author_id
    )

    assert updated.summary == "מעודכן"
    assert [strength.skill_name for strength in updated.strengths] == ["הבעה"]
    assert updated.plan_entries[0].solutions[0].solution_text_snapshot == "תרגול יומי"


def test_update_summary_is_audited_as_update(db_session: Session) -> None:
    fx = _setup(db_session)
    meeting = fx.service.create(fx.student_id, _request(), _ALL, fx.author_id)

    fx.service.update_summary(
        fx.student_id, meeting.id, MeetingUpdateRequest(summary="מעודכן"), _ALL, fx.author_id
    )

    actions = [log.action for log in db_session.scalars(select(AuditLog)).all()]
    assert AuditAction.UPDATE in actions


def test_update_summary_for_unknown_meeting_is_not_found(db_session: Session) -> None:
    fx = _setup(db_session)

    with pytest.raises(NotFoundError):
        fx.service.update_summary(
            fx.student_id, uuid.uuid4(), MeetingUpdateRequest(summary="x"), _ALL, fx.author_id
        )


def test_student_outside_scope_is_hidden(db_session: Session) -> None:
    fx = _setup(db_session)
    foreign_scope = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        fx.service.create(fx.student_id, _request(), foreign_scope, fx.author_id)
