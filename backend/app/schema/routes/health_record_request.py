import uuid
from datetime import date
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.models.client.health_session_type import HealthSessionType

_MAX_TEXT = 5000
_MAX_RESPONSIBLE = 20


class HealthRecordRequest(BaseModel):
    domain_id: uuid.UUID
    record_date: date
    session_type: HealthSessionType | None = None
    support_given: str = Field(default="", max_length=_MAX_TEXT)
    responsible_user_ids: list[uuid.UUID] = Field(default_factory=list, max_length=_MAX_RESPONSIBLE)
    notes: str = Field(default="", max_length=_MAX_TEXT)
    execution_review: str = Field(default="", max_length=_MAX_TEXT)

    @field_validator("responsible_user_ids")
    @classmethod
    def _unique(cls, values: list[uuid.UUID]) -> list[uuid.UUID]:
        return list(dict.fromkeys(values))

    @model_validator(mode="after")
    def _not_empty(self) -> Self:
        has_content = (
            self.session_type is not None
            or self.support_given.strip()
            or self.responsible_user_ids
            or self.notes.strip()
            or self.execution_review.strip()
        )
        if not has_content:
            raise ValueError("יש למלא לפחות שדה אחד בשורה")
        return self
