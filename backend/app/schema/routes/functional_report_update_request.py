from typing import Self

from pydantic import model_validator

from backend.app.schema.routes.functional_report_sections import FunctionalReportSections


class FunctionalReportUpdateRequest(FunctionalReportSections):
    @model_validator(mode="after")
    def _require_content(self) -> Self:
        if not any(getattr(self, name).strip() for name in self.section_names()):
            raise ValueError("יש למלא לפחות סעיף אחד בדוח")
        return self
