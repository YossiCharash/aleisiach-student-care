import uuid

from pydantic import BaseModel

from backend.app.schema.routes.social_note_entry_response import SocialNoteEntryResponse


class SocialNoteReportResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    entries: list[SocialNoteEntryResponse]
