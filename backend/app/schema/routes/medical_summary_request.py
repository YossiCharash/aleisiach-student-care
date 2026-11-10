from typing import Self

from pydantic import model_validator

from backend.app.models.client.medical_summary_options import MEDICAL_SUMMARY_OPTIONS
from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields


class MedicalSummaryRequest(MedicalSummaryFields):
    @model_validator(mode="after")
    def _known_unique_options(self) -> Self:
        for group, options in MEDICAL_SUMMARY_OPTIONS.items():
            allowed = {value for value, _ in options}
            chosen: list[str] = getattr(self, group)
            unknown = [value for value in chosen if value not in allowed]
            if unknown:
                raise ValueError(f"ערך לא מוכר בשדה {group}")
            setattr(self, group, list(dict.fromkeys(chosen)))
        return self
