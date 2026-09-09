from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.plan_entry_response import PlanEntryResponse
from backend.app.schema.routes.plan_response import PlanResponse
from backend.app.utils.service.document_shell import DocumentShell

_RATING_LABELS = {
    MeetingRating.YELLOW: "בהשגחה",
    MeetingRating.RED: "בתלות",
}


class PlanDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def to_html(self, plan: PlanResponse, institution_name: str) -> str:
        return self._shell.render(
            self._css(), institution_name, "תוכנית אישית", self._plan_section(plan)
        )

    def combined_html(self, plans: list[PlanResponse], institution_name: str) -> str:
        if not plans:
            body = '<p class="empty">אין תוכניות להצגה.</p>'
        else:
            body = "".join(self._plan_section(plan) for plan in reversed(plans))
        return self._shell.render(
            self._css(), institution_name, "תוכניות אישיות — כל התאריכים", body
        )

    def _plan_section(self, plan: PlanResponse) -> str:
        rows = "".join(self._row(entry) for entry in plan.entries)
        return (
            f'<h2 class="plan-date">{self._format_date(plan)}</h2>'
            "<table><thead><tr><th>מוקד לחיזוק</th><th>דירוג</th>"
            "<th>דרכי פתרון</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    def _row(self, entry: PlanEntryResponse) -> str:
        rating = _RATING_LABELS.get(entry.rating, "")
        solutions = (
            ", ".join(escape(item.solution_text_snapshot) for item in entry.solutions) or "—"
        )
        return (
            f"<tr><td>{escape(entry.skill_name_snapshot)}</td>"
            f"<td>{rating}</td><td>{solutions}</td></tr>"
        )

    def _format_date(self, plan: PlanResponse) -> str:
        return plan.created_at.strftime("%d/%m/%Y")

    def _css(self) -> str:
        return (
            f".plan-date{{color:{self._brand.primary_color};font-size:14pt;"
            "margin:0.8cm 0 0.3cm}"
            f".empty{{color:{self._brand.muted_color}}}"
            "table{width:100%;border-collapse:collapse;margin-bottom:0.4cm}"
            f"th,td{{border:1px solid {self._brand.accent_color};padding:6pt;text-align:right}}"
            f"th{{background:{self._brand.primary_color};color:{self._brand.surface_color}}}"
        )
