from datetime import date

from pydantic import BaseModel, Field

from backend.app.schema.routes.reception_checklist_item import ReceptionChecklistItem

_MAX_TEXT = 5000
_MAX_CODE = 100


class ReceptionReportUpsertRequest(BaseModel):
    committee_date: date | None = None
    committee_participants: str = Field(default="", max_length=_MAX_TEXT)
    intake_date: date | None = None
    committee_summary: str = Field(default="", max_length=_MAX_TEXT)
    committee_recommendations: str = Field(default="", max_length=_MAX_TEXT)
    framework_code: str = Field(default="", max_length=_MAX_CODE)
    tariff_code: str = Field(default="", max_length=_MAX_CODE)
    committee_held: ReceptionChecklistItem = Field(default_factory=ReceptionChecklistItem)
    director_approval: ReceptionChecklistItem = Field(default_factory=ReceptionChecklistItem)
    family_guardian_housing_updated: ReceptionChecklistItem = Field(
        default_factory=ReceptionChecklistItem
    )
    community_social_worker_updated: ReceptionChecklistItem = Field(
        default_factory=ReceptionChecklistItem
    )
    management_updated: ReceptionChecklistItem = Field(default_factory=ReceptionChecklistItem)
