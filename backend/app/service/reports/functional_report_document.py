from datetime import date
from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.functional_report_entry_response import (
    FunctionalReportEntryResponse,
)
from backend.app.schema.routes.functional_report_history_response import (
    FunctionalReportHistoryResponse,
)
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
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

    def single_html(self, history: FunctionalReportHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build("דוח תפקודי", issue, self._single_date(history))
        return self._render(history, meta, show_dates=False)

    def combined_html(self, history: FunctionalReportHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build("דוחות תפקודיים — כל התאריכים", issue)
        return self._render(history, meta, show_dates=True)

    def _single_date(self, history: FunctionalReportHistoryResponse) -> date | None:
        return history.entries[0].report_date if len(history.entries) == 1 else None

    def _render(
        self, history: FunctionalReportHistoryResponse, meta: DocumentMeta, show_dates: bool
    ) -> str:
        if not history.entries:
            entries = '<p class="empty">אין דוחות תפקודיים להצגה.</p>'
        else:
            entries = "".join(self._entry(entry, show_dates) for entry in history.entries)
        return self._shell.render(self._css(), meta, self._identity(history) + entries)

    def _identity(self, history: FunctionalReportHistoryResponse) -> str:
        return self._shell.field("מספר ת.ז", history.national_id) + self._shell.field(
            "תאריך לידה", self._shell.value(history.date_of_birth)
        )

    def _entry(self, entry: FunctionalReportEntryResponse, show_date: bool) -> str:
        heading = (
            f'<h1 class="entry-date">{self._shell.value(entry.report_date)}</h1>'
            if show_date
            else ""
        )
        return f'<div class="entry">{heading}{self._sections(entry)}{self._footer(entry)}</div>'

    def _sections(self, entry: FunctionalReportEntryResponse) -> str:
        return "".join(
            f"<h2>{escape(title)}</h2>"
            f'<div class="section-body">{self._shell.value(getattr(entry, field))}</div>'
            for field, title in _SECTION_TITLES
        )

    def _footer(self, entry: FunctionalReportEntryResponse) -> str:
        return (
            '<div class="footer">' + self._shell.field("נכתב על ידי", entry.author_name) + "</div>"
        )

    def _css(self) -> str:
        return (
            f".entry-date{{color:{self._brand.primary_color};font-size:16pt;margin:0.4cm 0 0}}"
            ".entry + .entry{page-break-before:always}"
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt;"
            "margin-top:16pt}"
            f".field{{margin:3pt 0}}.label{{color:{self._brand.muted_color}}}"
            ".section-body{white-space:pre-wrap;margin:4pt 0}"
            f".empty{{color:{self._brand.muted_color}}}"
            f".footer{{margin-top:24pt;border-top:1px solid {self._brand.muted_color};"
            "padding-top:8pt}"
        )
