from datetime import date

from pydantic import BaseModel, Field


class SocialNoteCreateRequest(BaseModel):
    note_date: date
    content: str = Field(min_length=1, max_length=5000)
