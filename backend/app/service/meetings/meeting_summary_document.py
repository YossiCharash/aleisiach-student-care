from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.schema.routes.plan_entry_response import PlanEntryResponse
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_strength import ProgramStrength
from backend.app.utils.service.document_shell import DocumentShell

_AREA_RATING_LABELS = {
    MeetingRating.YELLOW: "בהשגחה",
    MeetingRating.RED: "בתלות",
}


class MeetingSummaryDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def to_html(self, meeting: MeetingResponse, institution_name: str) -> str:
        body = (
            f'<p class="period">{meeting.meeting_date.strftime("%d/%m/%Y")}</p>'
            f"{self._strengths_section(meeting.strengths)}"
            f"{self._areas_section(meeting.areas_to_strengthen)}"
            f"{self._plan_section(meeting.plan_entries)}"
            f"{self._summary_section(meeting.summary)}"
        )
        return self._shell.render(self._css(), institution_name, "סיכום ישיבת צוות", body)

    def _strengths_section(self, strengths: list[ProgramStrength]) -> str:
        if not strengths:
            items = '<li class="empty">אין מוקדי כוח.</li>'
        else:
            items = "".join(f"<li>{escape(item.skill_name)}</li>" for item in strengths)
        return f'<h2>מוקדי כוח</h2><ul class="foci">{items}</ul>'

    def _areas_section(self, areas: list[ProgramArea]) -> str:
        if not areas:
            return '<h2>מוקדים לחיזוק</h2><p class="empty">אין מוקדים לחיזוק.</p>'
        rows = "".join(
            f"<tr><td>{escape(area.skill_name)}</td>"
            f"<td>{_AREA_RATING_LABELS.get(area.rating, '')}</td></tr>"
            for area in areas
        )
        return (
            "<h2>מוקדים לחיזוק</h2>"
            "<table><thead><tr><th>מוקד</th><th>דירוג</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    def _plan_section(self, entries: list[PlanEntryResponse]) -> str:
        if not entries:
            return '<h2>תוכנית אישית</h2><p class="empty">אין תוכנית אישית.</p>'
        rows = "".join(self._plan_row(entry) for entry in entries)
        return (
            "<h2>תוכנית אישית</h2>"
            "<table><thead><tr><th>מוקד לחיזוק</th><th>דירוג</th>"
            "<th>דרכי פתרון</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    def _plan_row(self, entry: PlanEntryResponse) -> str:
        rating = _AREA_RATING_LABELS.get(entry.rating, "")
        solutions = (
            ", ".join(escape(item.solution_text_snapshot) for item in entry.solutions) or "—"
        )
        return (
            f"<tr><td>{escape(entry.skill_name_snapshot)}</td>"
            f"<td>{rating}</td><td>{solutions}</td></tr>"
        )

    def _summary_section(self, summary: str) -> str:
        text = escape(summary).strip() or "—"
        return f'<h2>סיכום</h2><p class="summary">{text}</p>'

    def _css(self) -> str:
        return (
            f".period{{color:{self._brand.muted_color};margin-bottom:0.6cm}}"
            f"h2{{color:{self._brand.primary_color};font-size:14pt;margin:0.8cm 0 0.3cm}}"
            f".empty{{color:{self._brand.muted_color}}}"
            "ul.foci{margin:0;padding-inline-start:1.1cm}"
            ".summary{white-space:pre-wrap;line-height:1.5}"
            "table{width:100%;border-collapse:collapse;margin-bottom:0.4cm}"
            f"th,td{{border:1px solid {self._brand.accent_color};padding:6pt;text-align:right}}"
            f"th{{background:{self._brand.primary_color};color:{self._brand.surface_color}}}"
        )
