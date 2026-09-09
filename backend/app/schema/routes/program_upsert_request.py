from pydantic import BaseModel, Field

from backend.app.schema.routes.focus_rating_request import FocusRatingRequest


class ProgramUpsertRequest(BaseModel):
    entries: list[FocusRatingRequest] = Field(min_length=1)
