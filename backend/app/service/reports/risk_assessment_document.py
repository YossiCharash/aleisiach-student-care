import uuid
from datetime import date
from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.risk_labels import RISK_LEVEL_LABELS
from backend.app.schema.routes.risk_assessment_entry_response import RiskAssessmentEntryResponse
from backend.app.schema.routes.risk_assessment_history_response import (
    RiskAssessmentHistoryResponse,
)
from backend.app.schema.routes.risk_domain_response import RiskDomainResponse
from backend.app.schema.routes.risk_item_response import RiskItemResponse
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
from backend.app.utils.service.document_shell import DocumentShell

_TITLE = "ניהול סיכונים"

_COLUMNS = (
    "תחום הסיכון",
    "מהות הסיכון ודוגמא לאירועים שהיו בהקשר לסיכון",
    "רמת סיכון",
    "תוכנית ההתערבות המוצעת ולו״ז",
    "אחראי ביצוע",
)


class RiskAssessmentDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def single_html(self, history: RiskAssessmentHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build(_TITLE, issue, self._single_date(history))
        return self._render(history, meta, show_dates=False)

    def combined_html(self, history: RiskAssessmentHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build("ניהול סיכונים — כל התאריכים", issue)
        return self._render(history, meta, show_dates=True)

    def _single_date(self, history: RiskAssessmentHistoryResponse) -> date | None:
        return history.entries[0].assessment_date if len(history.entries) == 1 else None

    def _render(
        self, history: RiskAssessmentHistoryResponse, meta: DocumentMeta, show_dates: bool
    ) -> str:
        if not history.entries:
            body = '<p class="empty">אין טבלאות ניהול סיכונים להצגה.</p>'
        else:
            body = "".join(
                self._entry(history.domains, entry, show_dates) for entry in history.entries
            )
        return self._shell.render(self._css(), meta, body)

    def _entry(
        self,
        domains: list[RiskDomainResponse],
        entry: RiskAssessmentEntryResponse,
        show_date: bool,
    ) -> str:
        heading = (
            f'<h1 class="entry-date">{self._shell.value(entry.assessment_date)}</h1>'
            if show_date
            else ""
        )
        items = {item.domain_id: item for item in entry.items}
        header = "".join(f"<th>{escape(column)}</th>" for column in _COLUMNS)
        rows = "".join(self._rows(domains, items))
        footer = self._shell.field("נכתב על ידי", entry.author_name)
        return (
            f'<div class="entry">{heading}<table class="risks"><thead><tr>{header}</tr></thead>'
            f"<tbody>{rows}</tbody></table>{footer}</div>"
        )

    def _rows(
        self,
        domains: list[RiskDomainResponse],
        items: dict[uuid.UUID, RiskItemResponse],
    ) -> list[str]:
        rows: list[str] = []
        current_category: str | None = None
        for domain in domains:
            if not domain.is_active and domain.id not in items:
                continue
            if domain.category != current_category:
                current_category = domain.category
                rows.append(
                    f'<tr class="category"><td colspan="{len(_COLUMNS)}">'
                    f"{escape(domain.category_label)}</td></tr>"
                )
            rows.append(self._row(domain, items.get(domain.id)))
        return rows

    def _row(self, domain: RiskDomainResponse, item: RiskItemResponse | None) -> str:
        nature = item.nature if item is not None else ""
        level = RISK_LEVEL_LABELS[item.level] if item is not None and item.level else ""
        plan = item.intervention_plan if item is not None else ""
        responsible = (
            ", ".join(member.full_name for member in item.responsible) if item is not None else ""
        )
        cells = (domain.name, nature, level, plan, responsible)
        return "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in cells) + "</tr>"

    def _css(self) -> str:
        return (
            f".entry-date{{color:{self._brand.primary_color};font-size:16pt;margin:0.4cm 0 0}}"
            ".entry + .entry{page-break-before:always}"
            ".risks{width:100%;border-collapse:collapse;margin-top:8pt;font-size:9.5pt}"
            f".risks th{{background:{self._brand.primary_color};color:#ffffff;"
            "padding:4pt;text-align:right;vertical-align:bottom}"
            f".risks td{{border:1px solid {self._brand.muted_color};padding:4pt;"
            "vertical-align:top;white-space:pre-wrap}"
            ".risks tr{page-break-inside:avoid}"
            ".risks td:nth-child(1){width:22%}.risks td:nth-child(3){width:10%}"
            ".risks td:nth-child(5){width:14%}"
            f".risks .category td{{background:{self._brand.accent_color};color:#ffffff;"
            "font-weight:700;border-color:transparent}"
            f".field{{margin:10pt 0 3pt}}.label{{color:{self._brand.muted_color}}}"
            f".empty{{color:{self._brand.muted_color}}}"
        )
