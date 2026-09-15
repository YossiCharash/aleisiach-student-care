from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.functional_report_response import FunctionalReportResponse
from backend.app.utils.service.document_shell import DocumentShell

_SECTION_TITLES = (
    ("general_background", "רקע כללי"),
    ("vocational_domain", "התחום התעסוקתי"),
    ("behavioral_emotional_domain", "התחום ההתנהגותי-רגשי"),
    ("communication_social_domain", "התחום התקשורתי-חברתי"),
    ("independence_life_skills_domain", "תחום עצמאות וכישורי חיים"),
    ("summary_recommendations", "סיכום והמלצות"),
)


class FunctionalReportDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def _css(self) -> str:
        return (
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt;"
            "margin-top:16pt}"
            f".field{{margin:3pt 0}}.label{{color:{self._brand.muted_color}}}"
            ".section-body{white-space:pre-wrap;margin:4pt 0}"
            f".footer{{margin-top:24pt;border-top:1px solid {self._brand.muted_color};"
            "padding-top:8pt}"
        )

    def to_html(self, report: FunctionalReportResponse, institution_name: str) -> str:
        body = self._identity(report) + self._sections(report) + self._footer(report)
        return self._shell.render(self._css(), institution_name, "דוח תפקודי", body)

    def _identity(self, report: FunctionalReportResponse) -> str:
        return (
            self._shell.field("שם", report.student_name)
            + self._shell.field("מספר ת.ז", report.national_id)
            + self._shell.field("תאריך לידה", self._shell.value(report.date_of_birth))
        )

    def _sections(self, report: FunctionalReportResponse) -> str:
        return "".join(
            f"<h2>{escape(title)}</h2>"
            f'<div class="section-body">{self._shell.value(getattr(report, field))}</div>'
            for field, title in _SECTION_TITLES
        )

    def _footer(self, report: FunctionalReportResponse) -> str:
        return (
            '<div class="footer">'
            + self._shell.field("נכתב על ידי", report.written_by_name)
            + "</div>"
        )
