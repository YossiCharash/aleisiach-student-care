from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
from backend.app.utils.service.document_shell import DocumentShell

_RATING_LABELS = {
    MeetingRating.YELLOW: "בהשגחה",
    MeetingRating.RED: "בתלות",
}


class FociDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def to_html(self, program: ProgramResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build("מוקדי כוח ומוקדים לחיזוק", issue)
        if not program.exists:
            body = '<p class="empty">עדיין לא סומנו מוקדים.</p>'
        else:
            body = self._strengths_section(program) + self._areas_section(program)
        return self._shell.render(self._css(), meta, body)

    def _strengths_section(self, program: ProgramResponse) -> str:
        if not program.strengths:
            items = '<p class="empty">אין מוקדי כוח.</p>'
        else:
            rows = "".join(
                f"<li>{escape(strength.skill_name)}</li>" for strength in program.strengths
            )
            items = f'<ul class="strengths">{rows}</ul>'
        return f'<h2 class="section">מוקדי כוח</h2>{items}'

    def _areas_section(self, program: ProgramResponse) -> str:
        if not program.areas_to_strengthen:
            items = '<p class="empty">אין מוקדים לחיזוק.</p>'
        else:
            rows = "".join(self._area_row(area) for area in program.areas_to_strengthen)
            items = (
                "<table><thead><tr><th>מוקד לחיזוק</th><th>דירוג</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>"
            )
        return f'<h2 class="section">מוקדים לחיזוק</h2>{items}'

    def _area_row(self, area: ProgramArea) -> str:
        rating = _RATING_LABELS.get(area.rating, "")
        return f"<tr><td>{escape(area.skill_name)}</td><td>{rating}</td></tr>"

    def _css(self) -> str:
        return (
            f".section{{color:{self._brand.primary_color};font-size:14pt;"
            "margin:0.8cm 0 0.3cm}"
            f".empty{{color:{self._brand.muted_color}}}"
            ".strengths{margin:0;padding-right:0.6cm}"
            ".strengths li{padding:3pt 0}"
            "table{width:100%;border-collapse:collapse;margin-bottom:0.4cm}"
            f"th,td{{border:1px solid {self._brand.accent_color};padding:6pt;text-align:right}}"
            f"th{{background:{self._brand.primary_color};color:{self._brand.surface_color}}}"
        )
