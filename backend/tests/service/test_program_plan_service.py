import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.program.program_plan_repository import ProgramPlanRepository
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_plan_error import InvalidPlanError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.focus_rating_request import FocusRatingRequest
from backend.app.schema.routes.plan_create_request import PlanCreateRequest
from backend.app.schema.routes.plan_entry_request import PlanEntryRequest
from backend.app.schema.routes.program_upsert_request import ProgramUpsertRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.program.program_plan_service import ProgramPlanService
from backend.app.service.program.program_service import ProgramService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.taxonomy.skill_focus_resolver import SkillFocusResolver
from backend.tests.support.seeding import seed_actor

_ALL = StudentAccessScope(all_workshops=True)


class _Bundle:
    def __init__(
        self,
        plans: ProgramPlanService,
        program: ProgramService,
        student_id: uuid.UUID,
        author_id: uuid.UUID,
        skill_green: uuid.UUID,
        skill_area: uuid.UUID,
        solution_area: uuid.UUID,
    ) -> None:
        self.plans = plans
        self.program = program
        self.student_id = student_id
        self.author_id = author_id
        self.skill_green = skill_green
        self.skill_area = skill_area
        self.solution_area = solution_area


def _setup(session: Session) -> _Bundle:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    student = Student(full_name="Dana", workshop_id=workshop.id)
    session.add(student)
    label = Label(name="עצמאות")
    session.add(label)
    session.flush()
    skill_green = Skill(label_id=label.id, name="הבעה בעל פה")
    skill_area = Skill(label_id=label.id, name="הקשבה בקבוצה")
    session.add_all([skill_green, skill_area])
    session.flush()
    solution_area = Solution(
        skill_id=skill_area.id, text="ישיבה בקדמת הקבוצה", rating=MeetingRating.YELLOW
    )
    session.add(solution_area)
    session.flush()
    program = ProgramService(
        ProgramRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        SkillFocusResolver(TaxonomyRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )
    plans = ProgramPlanService(
        ProgramPlanRepository(session),
        ProgramRepository(session),
        TaxonomyRepository(session),
        StudentAccessGuard(StudentRepository(session)),
        AuditLogger(AuditLogRepository(session)),
    )
    bundle = _Bundle(
        plans,
        program,
        student.id,
        seed_actor(session),
        skill_green.id,
        skill_area.id,
        solution_area.id,
    )
    _seed_foci(bundle)
    return bundle


def _seed_foci(bundle: _Bundle) -> None:
    request = ProgramUpsertRequest(
        entries=[
            FocusRatingRequest(skill_id=bundle.skill_green, rating=MeetingRating.GREEN),
            FocusRatingRequest(skill_id=bundle.skill_area, rating=MeetingRating.YELLOW),
        ]
    )
    bundle.program.upsert(bundle.student_id, request, _ALL, bundle.author_id)


def _create_plan(bundle: _Bundle) -> uuid.UUID:
    request = PlanCreateRequest(
        entries=[PlanEntryRequest(skill_id=bundle.skill_area, solution_ids=[bundle.solution_area])]
    )
    return bundle.plans.create(bundle.student_id, request, _ALL, bundle.author_id).id


def test_create_snapshots_area_and_solutions(db_session: Session) -> None:
    bundle = _setup(db_session)

    plan_id = _create_plan(bundle)

    plan = bundle.plans.get(bundle.student_id, plan_id, _ALL)
    assert [entry.skill_id for entry in plan.entries] == [bundle.skill_area]
    assert plan.entries[0].rating == MeetingRating.YELLOW
    assert plan.entries[0].solutions[0].solution_text_snapshot == "ישיבה בקדמת הקבוצה"


def test_new_plan_keeps_previous_as_history(db_session: Session) -> None:
    bundle = _setup(db_session)
    first = _create_plan(bundle)
    second = _create_plan(bundle)

    plans = bundle.plans.list_for_student(bundle.student_id, _ALL)

    assert [plan.id for plan in plans][:2] == [second, first]
    assert len(plans) == 2


def test_create_is_audited(db_session: Session) -> None:
    bundle = _setup(db_session)
    _create_plan(bundle)

    logs = db_session.scalars(select(AuditLog).where(AuditLog.entity_type == "program_plan")).all()
    assert [log.action for log in logs] == [AuditAction.CREATE]


def test_plan_over_non_area_skill_is_rejected(db_session: Session) -> None:
    bundle = _setup(db_session)

    request = PlanCreateRequest(
        entries=[PlanEntryRequest(skill_id=bundle.skill_green, solution_ids=[bundle.solution_area])]
    )
    with pytest.raises(InvalidPlanError):
        bundle.plans.create(bundle.student_id, request, _ALL, bundle.author_id)


def test_solution_from_other_skill_is_rejected(db_session: Session) -> None:
    bundle = _setup(db_session)
    stray = Solution(skill_id=bundle.skill_green, text="לא שייך", rating=MeetingRating.YELLOW)
    db_session.add(stray)
    db_session.flush()

    request = PlanCreateRequest(
        entries=[PlanEntryRequest(skill_id=bundle.skill_area, solution_ids=[stray.id])]
    )
    with pytest.raises(InvalidPlanError):
        bundle.plans.create(bundle.student_id, request, _ALL, bundle.author_id)


def test_solution_with_mismatched_rating_is_rejected(db_session: Session) -> None:
    bundle = _setup(db_session)
    red_solution = Solution(skill_id=bundle.skill_area, text="פתרון אדום", rating=MeetingRating.RED)
    db_session.add(red_solution)
    db_session.flush()

    request = PlanCreateRequest(
        entries=[PlanEntryRequest(skill_id=bundle.skill_area, solution_ids=[red_solution.id])]
    )
    with pytest.raises(InvalidPlanError):
        bundle.plans.create(bundle.student_id, request, _ALL, bundle.author_id)


def test_plan_without_foci_is_rejected(db_session: Session) -> None:
    bundle = _setup(db_session)
    only_green = ProgramUpsertRequest(
        entries=[FocusRatingRequest(skill_id=bundle.skill_green, rating=MeetingRating.GREEN)]
    )
    bundle.program.upsert(bundle.student_id, only_green, _ALL, bundle.author_id)

    request = PlanCreateRequest(
        entries=[PlanEntryRequest(skill_id=bundle.skill_area, solution_ids=[bundle.solution_area])]
    )
    with pytest.raises(InvalidPlanError):
        bundle.plans.create(bundle.student_id, request, _ALL, bundle.author_id)


def test_get_plan_outside_scope_is_hidden(db_session: Session) -> None:
    bundle = _setup(db_session)
    plan_id = _create_plan(bundle)
    foreign = StudentAccessScope(all_workshops=False, workshop_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        bundle.plans.get(bundle.student_id, plan_id, foreign)
