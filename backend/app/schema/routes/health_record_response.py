import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from backend.app.models.client.health_session_type import HealthSessionType
from backend.app.schema.routes.staff_member_response import StaffMemberResponse


class HealthRecordResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    domain_id: uuid.UUID
    record_date: date
    session_type: HealthSessionType | None
    support_given: str
    responsible_user_ids: list[uuid.UUID]
    responsible: list[StaffMemberResponse] = Field(default_factory=list)
    notes: str
    execution_review: str
    author_id: uuid.UUID
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime
