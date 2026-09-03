from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.meeting_entry_response import MeetingEntryResponse
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.utils.service.document_shell import DocumentShell

_RATING_LABELS = {
    MeetingRating.GREEN: "עצמאי",
    MeetingRating.YELLOW: "בפיקוח",
    MeetingRating.RED: "תלוי",
}


class MeetingSummaryDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def to_html(self, meeting: MeetingResponse, institution_name: str) -> str:
        rows = "".join(self._row(entry) for entry in meeting.entries)
        body = (
            f'<p class="period">{meeting.month:02d}/{meeting.year}</p>'
            "<table><thead><tr><th>כישור</th><th>דירוג</th>"
            "<th>מוקדים לחיזוק</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
        return self._shell.render(self._css(), institution_name, "סיכום ישיבת צוות", body)

    def _css(self) -> str:
        return (
            f".period{{color:{self._brand.muted_color};margin-bottom:1cm}}"
            "table{width:100%;border-collapse:collapse}"
            f"th,td{{border:1px solid {self._brand.accent_color};padding:6pt;text-align:right}}"
            f"th{{background:{self._brand.primary_color};color:{self._brand.surface_color}}}"
        )

    def _row(self, entry: MeetingEntryResponse) -> str:
        rating = _RATING_LABELS[entry.rating]
        solutions = (
            ", ".join(escape(item.solution_text_snapshot) for item in entry.solutions) or "—"
        )
        return (
            f"<tr><td>{escape(entry.skill_name_snapshot)}</td>"
            f"<td>{rating}</td><td>{solutions}</td></tr>"
        )
