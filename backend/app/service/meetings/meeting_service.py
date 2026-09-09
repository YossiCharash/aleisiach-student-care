import uuid

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.program.program_plan_repository import ProgramPlanRepository
from backend.app.client.program.program_repository import ProgramRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.meeting_foci_entry import MeetingFociEntry
from backend.app.models.client.meeting_plan_entry import MeetingPlanEntry
from backend.app.models.client.meeting_plan_solution import MeetingPlanSolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program import Program
from backend.app.models.client.program_plan import ProgramPlan
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.schema.routes.meeting_update_request import MeetingUpdateRequest
from backend.app.schema.routes.plan_entry_response import PlanEntryResponse
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_strength import ProgramStrength
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard

_ENTITY_TYPE = "team_meeting"


class MeetingService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        program_repository: ProgramRepository,
        plan_repository: ProgramPlanRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
    ) -> None:
        self._meetings = meeting_repository
        self._programs = program_repository
        self._plans = plan_repository
        self._guard = access_guard
        self._audit = audit_logger

    def create(
        self,
        student_id: uuid.UUID,
        request: MeetingCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> MeetingResponse:
        self._guard.require(student_id, scope)
        program = self._programs.get_for_student(student_id)
        latest_plan = next(iter(self._plans.list_for_student(student_id)), None)
        meeting = TeamMeeting(
            student_id=student_id,
            meeting_date=request.meeting_date,
            summary=request.summary,
            author_id=author_id,
        )
        meeting.foci_entries = self._snapshot_foci(program)
        meeting.plan_entries = self._snapshot_plan(latest_plan)
        self._meetings.add(meeting)
        self._audit.record(
            AuditEntry(
                actor_id=author_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=meeting.id,
                changes=["meeting_date", "summary", "foci", "plan"],
            )
        )
        return self._to_response(meeting)

    def update_summary(
        self,
        student_id: uuid.UUID,
        meeting_id: uuid.UUID,
        request: MeetingUpdateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> MeetingResponse:
        self._guard.require(student_id, scope)
        meeting = self._meetings.get(meeting_id)
        if meeting is None or meeting.student_id != student_id:
            raise NotFoundError("meeting")
        meeting.summary = request.summary
        self._meetings.flush()
        self._audit.record(
            AuditEntry(
                actor_id=author_id,
                action=AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=meeting.id,
                changes=["summary"],
            )
        )
        return self._to_response(meeting)

    def list_for_student(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[MeetingResponse]:
        self._guard.require(student_id, scope)
        meetings = self._meetings.list_for_student(student_id)
        return [self._to_response(meeting) for meeting in meetings]

    def get(
        self, student_id: uuid.UUID, meeting_id: uuid.UUID, scope: StudentAccessScope
    ) -> MeetingResponse:
        self._guard.require(student_id, scope)
        meeting = self._meetings.get(meeting_id)
        if meeting is None or meeting.student_id != student_id:
            raise NotFoundError("meeting")
        return self._to_response(meeting)

    def _snapshot_foci(self, program: Program | None) -> list[MeetingFociEntry]:
        if program is None:
            return []
        return [
            MeetingFociEntry(
                skill_id=entry.skill_id,
                skill_name_snapshot=entry.skill_name_snapshot,
                rating=entry.rating,
                position=position,
            )
            for position, entry in enumerate(program.entries)
        ]

    def _snapshot_plan(self, plan: ProgramPlan | None) -> list[MeetingPlanEntry]:
        if plan is None:
            return []
        entries: list[MeetingPlanEntry] = []
        for position, source in enumerate(plan.entries):
            entry = MeetingPlanEntry(
                skill_id=source.skill_id,
                skill_name_snapshot=source.skill_name_snapshot,
                rating=source.rating,
                position=position,
            )
            entry.solutions = [
                MeetingPlanSolution(
                    solution_id=solution.solution_id,
                    solution_text_snapshot=solution.solution_text_snapshot,
                    position=solution_position,
                )
                for solution_position, solution in enumerate(source.solutions)
            ]
            entries.append(entry)
        return entries

    def _to_response(self, meeting: TeamMeeting) -> MeetingResponse:
        strengths: list[ProgramStrength] = []
        areas: list[ProgramArea] = []
        for entry in meeting.foci_entries:
            if entry.rating == MeetingRating.GREEN:
                strengths.append(
                    ProgramStrength(skill_id=entry.skill_id, skill_name=entry.skill_name_snapshot)
                )
            else:
                areas.append(
                    ProgramArea(
                        skill_id=entry.skill_id,
                        skill_name=entry.skill_name_snapshot,
                        rating=entry.rating,
                    )
                )
        return MeetingResponse(
            id=meeting.id,
            student_id=meeting.student_id,
            author_id=meeting.author_id,
            meeting_date=meeting.meeting_date,
            summary=meeting.summary,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at,
            strengths=strengths,
            areas_to_strengthen=areas,
            plan_entries=[
                PlanEntryResponse.model_validate(entry) for entry in meeting.plan_entries
            ],
        )
