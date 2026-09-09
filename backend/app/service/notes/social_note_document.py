from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.social_note_entry_response import SocialNoteEntryResponse
from backend.app.schema.routes.social_note_report_response import SocialNoteReportResponse
from backend.app.utils.service.document_shell import DocumentShell


class SocialNoteDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def combined_html(self, report: SocialNoteReportResponse, institution_name: str) -> str:
        return self._render(report, institution_name, "סיכומי עו״ס — כל התאריכים")

    def single_html(self, report: SocialNoteReportResponse, institution_name: str) -> str:
        return self._render(report, institution_name, "סיכום עו״ס")

    def _render(
        self, report: SocialNoteReportResponse, institution_name: str, title: str
    ) -> str:
        body = f'<p class="student">{escape(report.student_name)}</p>'
        if not report.entries:
            body += '<p class="empty">אין סיכומי עו״ס להצגה.</p>'
        else:
            body += "".join(self._entry_section(entry) for entry in report.entries)
        return self._shell.render(self._css(), institution_name, title, body)

    def _entry_section(self, entry: SocialNoteEntryResponse) -> str:
        author = escape(entry.author_name) if entry.author_name else "—"
        content = escape(entry.content).strip() or "—"
        return (
            f'<div class="entry"><h2>{entry.note_date.strftime("%d/%m/%Y")}</h2>'
            f'<p class="author">נכתב על ידי: {author}</p>'
            f'<p class="content">{content}</p></div>'
        )

    def _css(self) -> str:
        return (
            f".student{{color:{self._brand.muted_color};font-size:12pt;margin:0 0 0.4cm}}"
            f"h2{{color:{self._brand.primary_color};font-size:14pt;margin:0.6cm 0 0.1cm}}"
            f".author{{color:{self._brand.muted_color};font-size:10pt;margin:0 0 0.2cm}}"
            ".content{white-space:pre-wrap;line-height:1.5;margin:0}"
            f".empty{{color:{self._brand.muted_color}}}"
            f".entry{{border-bottom:1px solid {self._brand.accent_color};padding-bottom:0.4cm}}"
        )
