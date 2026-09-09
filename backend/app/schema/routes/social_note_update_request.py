from pydantic import BaseModel, Field


class SocialNoteUpdateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
