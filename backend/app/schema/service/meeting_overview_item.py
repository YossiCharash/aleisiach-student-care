import uuid

from pydantic import BaseModel


class MeetingOverviewItem(BaseModel):
    student_id: uuid.UUID
    student_name: str
    meeting_id: uuid.UUID
    year: int
    month: int
