import uuid
from datetime import date, datetime

from pydantic import BaseModel


class SocialNoteEntryResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    note_date: date
    content: str
    author_id: uuid.UUID
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime
