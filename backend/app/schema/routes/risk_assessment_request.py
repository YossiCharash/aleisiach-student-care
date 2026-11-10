from datetime import date
from typing import Self

from pydantic import BaseModel, Field, model_validator

from backend.app.schema.routes.risk_item_fields import RiskItemFields

_MAX_ITEMS = 200


class RiskAssessmentRequest(BaseModel):
    assessment_date: date
    items: list[RiskItemFields] = Field(default_factory=list, max_length=_MAX_ITEMS)

    @model_validator(mode="after")
    def _unique_domains(self) -> Self:
        domains = [item.domain_id for item in self.items]
        if len(domains) != len(set(domains)):
            raise ValueError("תחום סיכון מופיע יותר מפעם אחת")
        return self
