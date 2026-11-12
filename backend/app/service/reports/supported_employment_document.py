from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.work_style_labels import WORK_STYLE_LABELS
from backend.app.schema.routes.supported_employment_response import SupportedEmploymentResponse
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
from backend.app.utils.service.document_shell import DocumentShell

_FIELD_TITLES = (
    ("workplace", "מקום העבודה"),
    ("work_style", "סגנון עבודה"),
    ("address", "כתובת"),
    ("activity_type", "סוג הפעילות"),
    ("work_process", "תהליך העבודה"),
    ("work_environment", "סביבת העבודה"),
    ("required_body_functions", "תפקודי גוף נחוצים"),
    ("hazards_and_safety", "סכנות ובטיחות"),
    ("workplace_contact", "איש קשר במקום העבודה"),
    ("escort_contact", "איש קשר מלווה"),
    ("mobility", "ניידות"),
    ("work_hours", "שעת עבודה"),
)


class SupportedEmploymentDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def _css(self) -> str:
        return (
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt;"
            "margin-top:16pt}"
            ".section-body{white-space:pre-wrap;margin:4pt 0}"
        )

    def to_html(self, report: SupportedEmploymentResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build("ניתוח עבודה נתמכת", issue)
        body = self._fields(report)
        return self._shell.render(self._css(), meta, body)

    def _fields(self, report: SupportedEmploymentResponse) -> str:
        return "".join(
            f"<h2>{escape(title)}</h2>"
            f'<div class="section-body">{self._shell.value(self._text(report, field))}</div>'
            for field, title in _FIELD_TITLES
        )

    def _text(self, report: SupportedEmploymentResponse, field: str) -> str:
        if field == "work_style":
            return WORK_STYLE_LABELS[report.work_style] if report.work_style else ""
        text: str = getattr(report, field)
        return text
