from html import escape

from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.meeting_entry_response import MeetingEntryResponse
from backend.app.schema.routes.meeting_response import MeetingResponse

_RATING_LABELS = {
    MeetingRating.GREEN: "עצמאי",
    MeetingRating.YELLOW: "בפיקוח",
    MeetingRating.RED: "תלוי",
}

_CSS = (
    "body{font-family:'Heebo',sans-serif;direction:rtl;color:#333333;margin:2cm}"
    "h1{color:#CC3366;font-size:20pt}"
    ".institution{color:#5C5C5C;font-size:11pt;margin:0}"
    ".period{color:#5C5C5C;margin-bottom:1cm}"
    "table{width:100%;border-collapse:collapse}"
    "th,td{border:1px solid #85C441;padding:6pt;text-align:right}"
    "th{background:#85C441;color:#ffffff}"
)


class MeetingSummaryDocument:
    def to_html(self, meeting: MeetingResponse, institution_name: str) -> str:
        rows = "".join(self._row(entry) for entry in meeting.entries)
        return (
            '<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">'
            f"<style>{_CSS}</style></head><body>"
            f'<p class="institution">{escape(institution_name)}</p>'
            "<h1>סיכום ישיבת צוות</h1>"
            f'<p class="period">{meeting.month:02d}/{meeting.year}</p>'
            "<table><thead><tr><th>כישור</th><th>דירוג</th>"
            "<th>מוקדים לחיזוק</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></body></html>"
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
