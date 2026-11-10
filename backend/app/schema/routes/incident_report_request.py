from typing import Self

from pydantic import model_validator

from backend.app.schema.routes.incident_report_fields import IncidentReportFields


class IncidentReportRequest(IncidentReportFields):
    @model_validator(mode="after")
    def _require_description(self) -> Self:
        if not self.description.strip():
            raise ValueError("יש למלא את תיאור האירוע")
        return self
