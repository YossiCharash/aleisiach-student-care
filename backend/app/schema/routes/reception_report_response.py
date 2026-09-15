import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from backend.app.schema.routes.reception_checklist_item import ReceptionChecklistItem


class ReceptionReportResponse(BaseModel):
    student_id: uuid.UUID
    exists: bool = False
    student_name: str
    national_id: str | None = None
    date_of_birth: date | None = None
    committee_date: date | None = None
    committee_participants: str = ""
    intake_date: date | None = None
    committee_summary: str = ""
    committee_recommendations: str = ""
    framework_code: str = ""
    tariff_code: str = ""
    committee_held: ReceptionChecklistItem = Field(default_factory=ReceptionChecklistItem)
    director_approval: ReceptionChecklistItem = Field(default_factory=ReceptionChecklistItem)
    family_guardian_housing_updated: ReceptionChecklistItem = Field(
        default_factory=ReceptionChecklistItem
    )
    community_social_worker_updated: ReceptionChecklistItem = Field(
        default_factory=ReceptionChecklistItem
    )
    management_updated: ReceptionChecklistItem = Field(default_factory=ReceptionChecklistItem)
    written_by_name: str | None = None
    updated_at: datetime | None = None
