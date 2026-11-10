from datetime import date

from backend.app.schema.routes.functional_report_update_request import (
    FunctionalReportUpdateRequest,
)


class FunctionalReportCreateRequest(FunctionalReportUpdateRequest):
    report_date: date
