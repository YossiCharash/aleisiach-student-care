import uuid

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_meeting_error import InvalidMeetingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_entry_solution import MeetingEntrySolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.schema.routes.meeting_create_request import MeetingCreateRequest
from backend.app.schema.routes.meeting_entry_request import MeetingEntryRequest
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.schema.service.student_access_scope import StudentAccessScope

_RATINGS_REQUIRING_SOLUTION = frozenset({MeetingRating.YELLOW, MeetingRating.RED})


class MeetingService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        student_repository: StudentRepository,
        taxonomy_repository: TaxonomyRepository,
    ) -> None:
        self._meetings = meeting_repository
        self._students = student_repository
        self._taxonomy = taxonomy_repository

    def create(
        self,
        student_id: uuid.UUID,
        request: MeetingCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> MeetingResponse:
        self._require_student(student_id, scope)
        meeting = TeamMeeting(
            student_id=student_id,
            year=request.year,
            month=request.month,
            author_id=author_id,
        )
        meeting.entries = [self._build_entry(entry) for entry in request.entries]
        self._meetings.add(meeting)
        return MeetingResponse.model_validate(meeting)

    def list_for_student(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[MeetingResponse]:
        self._require_student(student_id, scope)
        meetings = self._meetings.list_for_student(student_id)
        return [MeetingResponse.model_validate(meeting) for meeting in meetings]

    def get(self, meeting_id: uuid.UUID, scope: StudentAccessScope) -> MeetingResponse:
        meeting = self._meetings.get(meeting_id)
        if meeting is None:
            raise NotFoundError("meeting")
        student = self._students.get(meeting.student_id)
        if student is None or not scope.permits(student.class_id):
            raise NotFoundError("meeting")
        return MeetingResponse.model_validate(meeting)

    def _require_student(self, student_id: uuid.UUID, scope: StudentAccessScope) -> Student:
        student = self._students.get(student_id)
        if student is None or not scope.permits(student.class_id):
            raise NotFoundError("student")
        return student

    def _build_entry(self, request: MeetingEntryRequest) -> MeetingEntry:
        skill = self._require_skill(request.skill_id)
        self._validate_rating(request)
        entry = MeetingEntry(
            skill_id=skill.id,
            skill_name_snapshot=skill.name,
            rating=request.rating,
        )
        entry.solutions = [
            self._build_solution(solution_id, skill) for solution_id in request.solution_ids
        ]
        return entry

    def _validate_rating(self, request: MeetingEntryRequest) -> None:
        needs_solution = request.rating in _RATINGS_REQUIRING_SOLUTION
        if needs_solution and not request.solution_ids:
            raise InvalidMeetingError("a solution is required for a yellow or red rating")
        if not needs_solution and request.solution_ids:
            raise InvalidMeetingError("a green rating cannot have solutions")

    def _build_solution(self, solution_id: uuid.UUID, skill: Skill) -> MeetingEntrySolution:
        solution = self._require_solution(solution_id)
        if solution.skill_id != skill.id:
            raise InvalidMeetingError("a solution does not belong to its skill")
        return MeetingEntrySolution(
            solution_id=solution.id,
            solution_text_snapshot=solution.text,
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
