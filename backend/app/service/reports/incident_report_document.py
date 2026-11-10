from collections.abc import Sequence
from datetime import date, time
from enum import StrEnum
from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.incident_nature import IncidentNature
from backend.app.models.client.incident_referral import IncidentReferral
from backend.app.models.client.incident_report_type import IncidentReportType
from backend.app.schema.routes.incident_report_entry_response import IncidentReportEntryResponse
from backend.app.schema.routes.incident_report_history_response import (
    IncidentReportHistoryResponse,
)
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
from backend.app.utils.service.document_shell import DocumentShell

_TITLE = "דו״ח אירוע חריג"

_REPORT_TYPES: dict[StrEnum, str] = {
    IncidentReportType.INTERNAL: "אירוע חריג – דיווח פנימי",
    IncidentReportType.EXTERNAL: "אירוע חריג – דיווח חיצוני",
}

_NATURES: dict[StrEnum, str] = {
    IncidentNature.ACCIDENT_INJURY_DEATH: "תאונה / פגיעה פיזית / פטירה",
    IncidentNature.VIOLENCE: "אלימות",
    IncidentNature.PROPERTY_DAMAGE: "פגיעה ברכוש",
    IncidentNature.PROHIBITED_SUBSTANCES: "שימוש בחומרים אסורים",
    IncidentNature.OTHER: "אחר",
}

_REFERRALS: dict[StrEnum, str] = {
    IncidentReferral.INTERNAL_EVENT: "אירוע פנימי",
    IncidentReferral.GUARDIAN: "אפוטרופוס / תומך החלטה",
    IncidentReferral.WELFARE_SOCIAL_WORKER: "עו״ס הרווחה",
    IncidentReferral.STATUTORY_SOCIAL_WORKER: "עו״ס על פי חוק",
    IncidentReferral.POLICE: "משטרה",
    IncidentReferral.FRAMEWORK_SUPERVISOR: "מפקח על המסגרת",
    IncidentReferral.OTHER: "אחר",
}

_EVENT_SECTIONS = (
    ("description", "תיאור האירוע"),
    ("staff_present", "אנשי צוות שנכחו באירוע"),
    ("affected_service_recipients", "מקבלי שירות שהיו נוכחים באירוע והושפעו מכך ובאיזה אופן"),
    ("warning_signs", "האם היו סימנים מקדימים לאירוע"),
    ("actions_taken", "סיכום הפעולות שבוצעו ע״י המדווח ואנשי הצוות האחרים"),
)

_LESSON_SECTIONS = (
    ("incident_causes", "הסיבות לאירוע"),
    ("was_preventable", "האם היה ניתן למנוע את האירוע"),
    ("lessons_learned", "לקחים שהופקו מהאירוע"),
    ("corrective_action_plan", "הכנת תכנית לפעולה מתקנת ליישום הלקחים"),
)

_ATTACHMENT_NOTE = "יש לצרף לטופס דו״ח מרפאה / משטרה / אחר (אם הייתה פנייה)"


class IncidentReportDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def single_html(self, history: IncidentReportHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build(_TITLE, issue, self._single_date(history))
        return self._render(history, meta, show_dates=False)

    def combined_html(self, history: IncidentReportHistoryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build("דו״חות אירוע חריג — כל התאריכים", issue)
        return self._render(history, meta, show_dates=True)

    def _single_date(self, history: IncidentReportHistoryResponse) -> date | None:
        return history.entries[0].event_date if len(history.entries) == 1 else None

    def _render(
        self, history: IncidentReportHistoryResponse, meta: DocumentMeta, show_dates: bool
    ) -> str:
        if not history.entries:
            body = '<p class="empty">אין דו״חות אירוע חריג להצגה.</p>'
        else:
            body = "".join(self._entry(history, entry, show_dates) for entry in history.entries)
        return self._shell.render(self._css(), meta, body)

    def _entry(
        self,
        history: IncidentReportHistoryResponse,
        entry: IncidentReportEntryResponse,
        show_date: bool,
    ) -> str:
        heading = (
            f'<h1 class="entry-date">{self._shell.value(entry.event_date)}</h1>'
            if show_date
            else ""
        )
        return (
            f'<div class="entry">{heading}{self._details(history, entry)}'
            f"{self._nature(entry)}{self._sections(entry, _EVENT_SECTIONS)}"
            f"{self._decision(entry)}{self._lessons(entry)}{self._footer(entry)}</div>"
        )

    def _details(
        self, history: IncidentReportHistoryResponse, entry: IncidentReportEntryResponse
    ) -> str:
        return (
            self._shell.field("שם מקבל השירות המעורב באירוע", self._recipient(history))
            + self._shell.field("תאריך האירוע", self._shell.value(entry.event_date))
            + self._shell.field("שעת האירוע", self._time(entry.event_time))
            + self._shell.field("מקום האירוע", entry.location)
            + self._shell.field("שם המדווח ותפקידו", entry.reporter_name_role)
        )

    def _recipient(self, history: IncidentReportHistoryResponse) -> str:
        if not history.national_id:
            return history.student_name
        return f"{history.student_name}, ת.ז {history.national_id}"

    def _nature(self, entry: IncidentReportEntryResponse) -> str:
        chosen_type = [entry.report_type] if entry.report_type is not None else []
        return (
            "<h2>מהות האירוע</h2>"
            '<div class="field"><span class="label">סוג האירוע:</span></div>'
            + self._checklist(_REPORT_TYPES, chosen_type, "")
            + self._checklist(_NATURES, entry.natures, entry.nature_other)
        )

    def _decision(self, entry: IncidentReportEntryResponse) -> str:
        return (
            "<h2>החלטה</h2>"
            '<div class="field"><span class="label">האירוע הועבר ל:</span></div>'
            + self._checklist(_REFERRALS, entry.referrals, entry.referral_other)
            + self._section("נימוקים להחלטה", entry.decision_reasons)
            + self._shell.field(
                "מנהל המפעל / מנהל מקצועי עודכן בתאריך",
                self._manager_updated(entry),
            )
        )

    def _manager_updated(self, entry: IncidentReportEntryResponse) -> str:
        on_date = (
            self._shell.value(entry.manager_updated_date) if entry.manager_updated_date else ""
        )
        at_time = (
            f"בשעה {self._time(entry.manager_updated_time)}" if entry.manager_updated_time else ""
        )
        return " ".join(part for part in (on_date, at_time) if part)

    def _lessons(self, entry: IncidentReportEntryResponse) -> str:
        return "<h2>הפקת לקחים מהאירוע</h2>" + self._sections(entry, _LESSON_SECTIONS)

    def _checklist(
        self, options: dict[StrEnum, str], chosen: Sequence[StrEnum], other_text: str
    ) -> str:
        items = []
        for option, label in options.items():
            checked = option in chosen
            text = escape(label)
            if option.value == "other" and checked and other_text:
                text += f": {escape(other_text)}"
            box = "box checked" if checked else "box"
            items.append(f'<li><span class="{box}"></span>{text}</li>')
        return f'<ul class="checklist">{"".join(items)}</ul>'

    def _sections(
        self, entry: IncidentReportEntryResponse, sections: tuple[tuple[str, str], ...]
    ) -> str:
        return "".join(self._section(title, getattr(entry, field)) for field, title in sections)

    def _section(self, title: str, body: str) -> str:
        return (
            f"<h3>{escape(title)}</h3>" f'<div class="section-body">{self._shell.value(body)}</div>'
        )

    def _footer(self, entry: IncidentReportEntryResponse) -> str:
        return (
            '<div class="footer">'
            + self._shell.field("שם ממלא הטופס", entry.filler_name)
            + self._shell.field("תפקיד", entry.filler_role)
            + '<div class="field signature"><span class="label">חתימה: </span>'
            '<span class="signature-line"></span></div>'
            f'<p class="note">{escape(_ATTACHMENT_NOTE)}</p>'
            "</div>"
        )

    def _time(self, value: time | None) -> str:
        return value.strftime("%H:%M") if value is not None else ""

    def _css(self) -> str:
        return (
            f".entry-date{{color:{self._brand.primary_color};font-size:16pt;margin:0.4cm 0 0}}"
            ".entry + .entry{page-break-before:always}"
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt;"
            "margin-top:16pt}"
            f"h3{{color:{self._brand.primary_color};font-size:11.5pt;margin:10pt 0 2pt}}"
            f".field{{margin:3pt 0}}.label{{color:{self._brand.muted_color}}}"
            ".section-body{white-space:pre-wrap;margin:2pt 0 4pt}"
            ".checklist{list-style:none;margin:2pt 0 6pt;padding:0}"
            ".checklist li{margin:3pt 0}"
            f".box{{display:inline-block;width:9pt;height:9pt;border:1pt solid "
            f"{self._brand.text_color};margin-left:6pt;vertical-align:middle}}"
            f".box.checked{{background:{self._brand.primary_color};"
            f"border-color:{self._brand.primary_color}}}"
            f".empty{{color:{self._brand.muted_color}}}"
            f".footer{{margin-top:24pt;border-top:1px solid {self._brand.muted_color};"
            "padding-top:8pt}"
            ".signature{margin-top:14pt}"
            ".signature-line{display:inline-block;width:5cm;"
            f"border-bottom:1px solid {self._brand.text_color}}}"
            f".note{{color:{self._brand.muted_color};font-size:9.5pt;margin-top:12pt}}"
        )
