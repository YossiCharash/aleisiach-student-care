from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.health_session_type_labels import HEALTH_SESSION_TYPE_LABELS
from backend.app.schema.routes.health_domain_response import HealthDomainResponse
from backend.app.schema.routes.health_record_history_response import (
    HealthRecordHistoryResponse,
)
from backend.app.schema.routes.health_record_response import HealthRecordResponse
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
from backend.app.utils.service.document_shell import DocumentShell

TITLE = "תיעוד אישי – מקצועות הבריאות"

_COLUMNS = (
    "תאריך",
    "אישי/קבוצתי",
    "תמיכה שניתנה",
    "אחראי ביצוע",
    "הערות",
    "בקרת ביצוע",
)


class HealthRecordDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def html(self, history: HealthRecordHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build(TITLE, issue)
        tables = [
            self._table(domain, records)
            for domain in history.domains
            if (records := [entry for entry in history.entries if entry.domain_id == domain.id])
        ]
        body = "".join(tables) or '<p class="empty">אין רשומות תיעוד להצגה.</p>'
        return self._shell.render(self._css(), meta, body)

    def _table(self, domain: HealthDomainResponse, records: list[HealthRecordResponse]) -> str:
        header = "".join(f"<th>{escape(column)}</th>" for column in _COLUMNS)
        rows = "".join(self._row(record) for record in records)
        return (
            f'<div class="domain"><h1 class="domain-name">תחום: {escape(domain.name)}</h1>'
            f'<table class="records"><thead><tr>{header}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>"
        )

    def _row(self, record: HealthRecordResponse) -> str:
        session_type = (
            HEALTH_SESSION_TYPE_LABELS[record.session_type] if record.session_type else ""
        )
        responsible = ", ".join(member.full_name for member in record.responsible)
        cells = (
            self._shell.value(record.record_date),
            session_type,
            record.support_given,
            responsible,
            record.notes,
            record.execution_review,
        )
        return "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in cells) + "</tr>"

    def _css(self) -> str:
        return (
            f".domain-name{{color:{self._brand.primary_color};font-size:15pt;margin:0.4cm 0 0}}"
            ".domain + .domain{page-break-before:always}"
            ".records{width:100%;border-collapse:collapse;margin-top:8pt;font-size:9.5pt}"
            f".records th{{background:{self._brand.primary_color};color:#ffffff;"
            "padding:4pt;text-align:right;vertical-align:bottom}"
            f".records td{{border:1px solid {self._brand.muted_color};padding:4pt;"
            "vertical-align:top;white-space:pre-wrap}"
            ".records tr{page-break-inside:avoid}"
            ".records td:nth-child(1){width:11%}.records td:nth-child(2){width:9%}"
            ".records td:nth-child(4){width:14%}"
            f".empty{{color:{self._brand.muted_color}}}"
        )
