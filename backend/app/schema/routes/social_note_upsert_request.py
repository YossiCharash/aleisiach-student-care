from pydantic import BaseModel, Field


class SocialNoteUpsertRequest(BaseModel):
    content: str = Field(max_length=5000)
