import uuid

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_meeting_error import InvalidMeetingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_entry_solution import MeetingEntrySolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_entry_request import MeetingEntryRequest
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard

_RATINGS_REQUIRING_SOLUTION = frozenset({MeetingRating.YELLOW, MeetingRating.RED})
_ENTITY_TYPE = "team_meeting"


class MeetingService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        access_guard: StudentAccessGuard,
        taxonomy_repository: TaxonomyRepository,
        audit_logger: AuditLogger,
    ) -> None:
        self._meetings = meeting_repository
        self._guard = access_guard
        self._taxonomy = taxonomy_repository
        self._audit = audit_logger

    def create(
        self,
        student_id: uuid.UUID,
        request: MeetingCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> MeetingResponse:
        self._guard.require(student_id, scope)
        self._reject_duplicate_skills(request)
        meeting = TeamMeeting(
            student_id=student_id,
            year=request.year,
            month=request.month,
            author_id=author_id,
        )
        meeting.entries = [
            self._build_entry(position, entry) for position, entry in enumerate(request.entries)
        ]
        self._meetings.add(meeting)
        self._audit.record(
            AuditEntry(
                actor_id=author_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=meeting.id,
                changes=["year", "month", "entries"],
            )
        )
        return MeetingResponse.model_validate(meeting)

    def list_for_student(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[MeetingResponse]:
        self._guard.require(student_id, scope)
        meetings = self._meetings.list_for_student(student_id)
        return [MeetingResponse.model_validate(meeting) for meeting in meetings]

    def get(
        self, student_id: uuid.UUID, meeting_id: uuid.UUID, scope: StudentAccessScope
    ) -> MeetingResponse:
        self._guard.require(student_id, scope)
        meeting = self._meetings.get(meeting_id)
        if meeting is None or meeting.student_id != student_id:
            raise NotFoundError("meeting")
        return MeetingResponse.model_validate(meeting)

    def _reject_duplicate_skills(self, request: MeetingCreateRequest) -> None:
        skill_ids = [entry.skill_id for entry in request.entries]
        if len(set(skill_ids)) != len(skill_ids):
            raise InvalidMeetingError("a skill appears more than once in the meeting")

    def _build_entry(self, position: int, request: MeetingEntryRequest) -> MeetingEntry:
        skill = self._require_skill(request.skill_id)
        self._validate_rating(request)
        self._reject_duplicate_solutions(request)
        entry = MeetingEntry(
            skill_id=skill.id,
            skill_name_snapshot=skill.name,
            rating=request.rating,
            position=position,
        )
        entry.solutions = [
            self._build_solution(solution_position, solution_id, skill)
            for solution_position, solution_id in enumerate(request.solution_ids)
        ]
        return entry

    def _validate_rating(self, request: MeetingEntryRequest) -> None:
        needs_solution = request.rating in _RATINGS_REQUIRING_SOLUTION
        if needs_solution and not request.solution_ids:
            raise InvalidMeetingError("a solution is required for a yellow or red rating")
        if not needs_solution and request.solution_ids:
            raise InvalidMeetingError("a green rating cannot have solutions")

    def _reject_duplicate_solutions(self, request: MeetingEntryRequest) -> None:
        if len(set(request.solution_ids)) != len(request.solution_ids):
            raise InvalidMeetingError("a solution was chosen more than once")

    def _build_solution(
        self, position: int, solution_id: uuid.UUID, skill: Skill
    ) -> MeetingEntrySolution:
        solution = self._require_solution(solution_id)
        if solution.skill_id != skill.id:
            raise InvalidMeetingError("a solution does not belong to its skill")
        return MeetingEntrySolution(
            solution_id=solution.id,
            solution_text_snapshot=solution.text,
            position=position,
        )

    def _require_skill(self, skill_id: uuid.UUID) -> Skill:
        skill = self._taxonomy.get_skill(skill_id)
        if skill is None:
            raise NotFoundError("skill")
        return skill

    def _require_solution(self, solution_id: uuid.UUID) -> Solution:
        solution = self._taxonomy.get_solution(solution_id)
        if solution is None:
            raise NotFoundError("solution")
        return solution
