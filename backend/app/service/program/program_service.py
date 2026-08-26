import uuid

from backend.app.client.meetings.meeting_repository import MeetingRepository
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.schema.routes.program_strength import ProgramStrength
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.students.student_access_guard import StudentAccessGuard


class ProgramService:
    def __init__(
        self, meeting_repository: MeetingRepository, access_guard: StudentAccessGuard
    ) -> None:
        self._meetings = meeting_repository
        self._guard = access_guard

    def get_for_student(self, student_id: uuid.UUID, scope: StudentAccessScope) -> ProgramResponse:
        self._guard.require(student_id, scope)
        strengths: list[ProgramStrength] = []
        areas: list[ProgramArea] = []
        seen: set[uuid.UUID] = set()
        for meeting in self._meetings.list_for_student(student_id):
            for entry in meeting.entries:
                if entry.skill_id in seen:
                    continue
                seen.add(entry.skill_id)
                if entry.rating == MeetingRating.GREEN:
                    strengths.append(self._strength(entry, meeting))
                else:
                    areas.append(self._area(entry, meeting))
        return ProgramResponse(
            student_id=student_id, strengths=strengths, areas_to_strengthen=areas
        )

    def _strength(self, entry: MeetingEntry, meeting: TeamMeeting) -> ProgramStrength:
        return ProgramStrength(
            skill_id=entry.skill_id,
            skill_name=entry.skill_name_snapshot,
            year=meeting.year,
            month=meeting.month,
        )

    def _area(self, entry: MeetingEntry, meeting: TeamMeeting) -> ProgramArea:
        return ProgramArea(
            skill_id=entry.skill_id,
            skill_name=entry.skill_name_snapshot,
            rating=entry.rating,
            solutions=[solution.solution_text_snapshot for solution in entry.solutions],
            year=meeting.year,
            month=meeting.month,
        )
