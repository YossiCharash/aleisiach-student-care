from datetime import date, time
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from backend.app.models.client.incident_nature import IncidentNature
from backend.app.models.client.incident_referral import IncidentReferral
from backend.app.models.client.incident_report_type import IncidentReportType

_MAX_TEXT = 5000
_MAX_SHORT = 300


class IncidentReportFields(BaseModel):
    event_date: date
    event_time: time | None = None
    location: str = Field(default="", max_length=_MAX_SHORT)
    reporter_name_role: str = Field(default="", max_length=_MAX_SHORT)
    report_type: IncidentReportType | None = None
    natures: list[IncidentNature] = Field(default_factory=list)
    nature_other: str = Field(default="", max_length=_MAX_SHORT)
    description: str = Field(default="", max_length=_MAX_TEXT)
    staff_present: str = Field(default="", max_length=_MAX_TEXT)
    affected_service_recipients: str = Field(default="", max_length=_MAX_TEXT)
    warning_signs: str = Field(default="", max_length=_MAX_TEXT)
    actions_taken: str = Field(default="", max_length=_MAX_TEXT)
    referrals: list[IncidentReferral] = Field(default_factory=list)
    referral_other: str = Field(default="", max_length=_MAX_SHORT)
    decision_reasons: str = Field(default="", max_length=_MAX_TEXT)
    manager_updated_date: date | None = None
    manager_updated_time: time | None = None
    incident_causes: str = Field(default="", max_length=_MAX_TEXT)
    was_preventable: str = Field(default="", max_length=_MAX_TEXT)
    lessons_learned: str = Field(default="", max_length=_MAX_TEXT)
    corrective_action_plan: str = Field(default="", max_length=_MAX_TEXT)
    filler_role: str = Field(default="", max_length=_MAX_SHORT)

    @field_validator("natures", "referrals")
    @classmethod
    def _unique(cls, values: list[StrEnum]) -> list[StrEnum]:
        return list(dict.fromkeys(values))

    @classmethod
    def field_names(cls) -> tuple[str, ...]:
        return tuple(IncidentReportFields.model_fields)
