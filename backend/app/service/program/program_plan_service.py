import uuid

from backend.app.client.program.program_plan_repository import ProgramPlanRepository
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_plan_error import InvalidPlanError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program_entry import ProgramEntry
from backend.app.models.client.program_plan import ProgramPlan
from backend.app.models.client.program_plan_entry import ProgramPlanEntry
from backend.app.models.client.program_plan_solution import ProgramPlanSolution
from backend.app.schema.routes.plan_create_request import PlanCreateRequest
from backend.app.schema.routes.plan_entry_request import PlanEntryRequest
from backend.app.schema.routes.plan_response import PlanResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.resolved_plan_entry import ResolvedPlanEntry
from backend.app.schema.service.resolved_solution import ResolvedSolution
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard

_ENTITY_TYPE = "program_plan"
_AREA_RATINGS = frozenset({MeetingRating.YELLOW, MeetingRating.RED})


class ProgramPlanService:
    def __init__(
        self,
        plan_repository: ProgramPlanRepository,
        program_repository: ProgramRepository,
        taxonomy_repository: TaxonomyRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
    ) -> None:
        self._plans = plan_repository
        self._programs = program_repository
        self._taxonomy = taxonomy_repository
        self._guard = access_guard
        self._audit = audit_logger

    def list_for_student(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[PlanResponse]:
        self._guard.require(student_id, scope)
        plans = self._plans.list_for_student(student_id)
        return [PlanResponse.model_validate(plan) for plan in plans]

    def get(
        self, student_id: uuid.UUID, plan_id: uuid.UUID, scope: StudentAccessScope
    ) -> PlanResponse:
        self._guard.require(student_id, scope)
        plan = self._plans.get(plan_id)
        if plan is None or plan.student_id != student_id:
            raise NotFoundError("plan")
        return PlanResponse.model_validate(plan)

    def create(
        self,
        student_id: uuid.UUID,
        request: PlanCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> PlanResponse:
        self._guard.require(student_id, scope)
        areas = self._current_areas(student_id)
        resolved = self._resolve_entries(request, areas)
        plan = ProgramPlan(student_id=student_id, author_id=author_id)
        plan.entries = [self._build_entry(position, item) for position, item in enumerate(resolved)]
        self._plans.add(plan)
        self._audit.record(
            AuditEntry(
                actor_id=author_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=plan.id,
                changes=["entries"],
            )
        )
        return PlanResponse.model_validate(plan)

    def _current_areas(self, student_id: uuid.UUID) -> dict[uuid.UUID, ProgramEntry]:
        program = self._programs.get_for_student(student_id)
        if program is None:
            raise InvalidPlanError("אין מוקדים לתלמיד — יש ליצור מוקדים לפני בניית תוכנית.")
        areas = {
            entry.skill_id: entry for entry in program.entries if entry.rating in _AREA_RATINGS
        }
        if not areas:
            raise InvalidPlanError("אין מוקדים לחיזוק לבניית תוכנית.")
        return areas

    def _resolve_entries(
        self, request: PlanCreateRequest, areas: dict[uuid.UUID, ProgramEntry]
    ) -> list[ResolvedPlanEntry]:
        self._reject_duplicate_skills(request.entries)
        return [self._resolve_entry(entry, areas) for entry in request.entries]

    def _resolve_entry(
        self, entry: PlanEntryRequest, areas: dict[uuid.UUID, ProgramEntry]
    ) -> ResolvedPlanEntry:
        area = areas.get(entry.skill_id)
        if area is None:
            raise InvalidPlanError("נבחר כישור שאינו מוקד לחיזוק.")
        self._reject_duplicate_solutions(entry)
        solutions = [
            self._resolve_solution(solution_id, entry.skill_id)
            for solution_id in entry.solution_ids
        ]
        return ResolvedPlanEntry(
            skill_id=area.skill_id,
            skill_name=area.skill_name_snapshot,
            rating=area.rating,
            solutions=solutions,
        )

    def _resolve_solution(self, solution_id: uuid.UUID, skill_id: uuid.UUID) -> ResolvedSolution:
        solution = self._taxonomy.get_solution(solution_id)
        if solution is None:
            raise NotFoundError("solution")
        if solution.skill_id != skill_id:
            raise InvalidPlanError("פתרון שנבחר אינו שייך לכישור שלו.")
        return ResolvedSolution(solution_id=solution.id, solution_text=solution.text)

    def _reject_duplicate_skills(self, entries: list[PlanEntryRequest]) -> None:
        skill_ids = [entry.skill_id for entry in entries]
        if len(set(skill_ids)) != len(skill_ids):
            raise InvalidPlanError("כישור מופיע יותר מפעם אחת.")

    def _reject_duplicate_solutions(self, entry: PlanEntryRequest) -> None:
        if len(set(entry.solution_ids)) != len(entry.solution_ids):
            raise InvalidPlanError("פתרון נבחר יותר מפעם אחת.")

    def _build_entry(self, position: int, resolved: ResolvedPlanEntry) -> ProgramPlanEntry:
        entry = ProgramPlanEntry(
            skill_id=resolved.skill_id,
            skill_name_snapshot=resolved.skill_name,
            rating=resolved.rating,
            position=position,
        )
        entry.solutions = [
            ProgramPlanSolution(
                solution_id=solution.solution_id,
                solution_text_snapshot=solution.solution_text,
                position=solution_position,
            )
            for solution_position, solution in enumerate(resolved.solutions)
        ]
        return entry
