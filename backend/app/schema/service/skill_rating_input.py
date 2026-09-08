import uuid
from typing import Protocol

from backend.app.models.client.meeting_rating import MeetingRating


class SkillRatingInput(Protocol):
    skill_id: uuid.UUID
    rating: MeetingRating
    solution_ids: list[uuid.UUID]
