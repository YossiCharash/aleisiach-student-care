from typing import Annotated

from pydantic import BaseModel, StringConstraints

RatingText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class SkillRatingsInput(BaseModel):
    green: RatingText
    yellow: RatingText
    red: RatingText
