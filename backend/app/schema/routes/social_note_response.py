import uuid
from datetime import datetime

from pydantic import BaseModel


class SocialNoteResponse(BaseModel):
    student_id: uuid.UUID
    content: str | None = None
    updated_by: uuid.UUID | None = None
    updated_at: datetime | None = None
