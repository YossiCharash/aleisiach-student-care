from typing import Self

from pydantic import model_validator

from backend.app.models.client.incident_nature import IncidentNature
from backend.app.models.client.incident_referral import IncidentReferral
from backend.app.schema.routes.incident_report_fields import IncidentReportFields


class IncidentReportRequest(IncidentReportFields):
    @model_validator(mode="after")
    def _require_description(self) -> Self:
        if not self.description.strip():
            raise ValueError("יש למלא את תיאור האירוע")
        return self

    @model_validator(mode="after")
    def _drop_unselected_other_text(self) -> Self:
        if IncidentNature.OTHER not in self.natures:
            self.nature_other = ""
        if IncidentReferral.OTHER not in self.referrals:
            self.referral_other = ""
        return self
