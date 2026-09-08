import uuid

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_entry_solution import MeetingEntrySolution
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.resolved_skill_rating import ResolvedSkillRating
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.taxonomy.skill_rating_resolver import SkillRatingResolver

_ENTITY_TYPE = "team_meeting"


class MeetingService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        access_guard: StudentAccessGuard,
        resolver: SkillRatingResolver,
        audit_logger: AuditLogger,
    ) -> None:
        self._meetings = meeting_repository
        self._guard = access_guard
        self._resolver = resolver
        self._audit = audit_logger

    def create(
        self,
        student_id: uuid.UUID,
        request: MeetingCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> MeetingResponse:
        self._guard.require(student_id, scope)
        resolved = self._resolver.resolve(request.entries)
        meeting = TeamMeeting(
            student_id=student_id,
            year=request.year,
            month=request.month,
            author_id=author_id,
        )
        meeting.entries = [
            self._build_entry(position, item) for position, item in enumerate(resolved)
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

    def _build_entry(self, position: int, resolved: ResolvedSkillRating) -> MeetingEntry:
        entry = MeetingEntry(
            skill_id=resolved.skill_id,
            skill_name_snapshot=resolved.skill_name,
            rating=resolved.rating,
            position=position,
        )
        entry.solutions = [
            MeetingEntrySolution(
                solution_id=solution.solution_id,
                solution_text_snapshot=solution.solution_text,
                position=solution_position,
            )
            for solution_position, solution in enumerate(resolved.solutions)
        ]
        return entry
