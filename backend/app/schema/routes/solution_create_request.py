import uuid

from pydantic import BaseModel, Field, field_validator

from backend.app.models.client.meeting_rating import MeetingRating

_ALLOWED_RATINGS = frozenset({MeetingRating.YELLOW, MeetingRating.RED})


class SolutionCreateRequest(BaseModel):
    skill_id: uuid.UUID
    text: str = Field(min_length=1, max_length=500)
    rating: MeetingRating

    @field_validator("rating")
    @classmethod
    def _only_area_ratings(cls, value: MeetingRating) -> MeetingRating:
        if value not in _ALLOWED_RATINGS:
            raise ValueError("דרך עבודה ניתן להוסיף רק לדירוג צהוב או אדום.")
        return value
