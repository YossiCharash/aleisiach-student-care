import uuid
from datetime import date, datetime

from pydantic import BaseModel


class FunctionalReportResponse(BaseModel):
    student_id: uuid.UUID
    exists: bool = False
    student_name: str
    national_id: str | None = None
    date_of_birth: date | None = None
    general_background: str = ""
    vocational_domain: str = ""
    behavioral_emotional_domain: str = ""
    communication_social_domain: str = ""
    independence_life_skills_domain: str = ""
    summary_recommendations: str = ""
    written_by_name: str | None = None
    updated_at: datetime | None = None
