from collections.abc import Sequence
from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.medical_summary_options import MEDICAL_SUMMARY_OPTIONS
from backend.app.schema.routes.medical_summary_response import MedicalSummaryResponse
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext
from backend.app.utils.service.document_shell import DocumentShell

TITLE = "סיכום מידע רפואי"

_YES_NO = (("yes", "כן"), ("no", "לא"))

_MEDICAL_TEXTS = (
    ("allergies", "רגישויות / אלרגיה ידועה"),
    ("known_syndrome", "ידוע על תסמונת"),
    ("background_diseases", "מחלות רקע"),
    ("hospitalizations_surgeries", "אשפוזים / ניתוחים בעבר"),
)

_FUNCTION_GROUPS = (
    ("comprehension", "הבנה"),
    ("communication", "שפה ותקשורת"),
    ("speech", "דיבור"),
    ("vision", "ראייה"),
    ("hearing", "שמיעה"),
    ("functioning", "תפקוד"),
    ("mobility", "ניידות"),
    ("eating", "אכילה"),
)

_NOURISHMENT_GROUPS = (
    ("chewing_swallowing", "לעיסה / בליעה"),
    ("food_texture", "התאמת מרקמי מזון"),
)

_GOOD_TO_KNOW = (
    ("loves", "דברים שאוהב במיוחד"),
    ("calming", "דברים שמרגיעים אותו"),
    ("angering", "דברים שמכעיסים אותו"),
    ("frightening", "דברים שמפחידים אותו"),
    ("stress_behavior", "מאפייני התנהגות במצבי דחק"),
    ("care_recommendations", "המלצות מהצוות הטיפולי הישיר"),
    ("general_notes", "הערות כלליות"),
)

_OTHER_TEXTS: dict[str, tuple[str, str]] = {
    "communication": ("alternative", "communication_other"),
    "diet": ("other", "diet_other"),
}

_MEDICATION_NOTE = "תרופות קבועות ומידע נוסף מפורט במכתב הרפואי המצורף"


class MedicalSummaryDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def to_html(self, summary: MedicalSummaryResponse, issue: IssueContext) -> str:
        meta = DocumentMeta.build(TITLE, issue)
        body = (
            self._personal(summary)
            + self._medical(summary)
            + self._functioning(summary)
            + self._good_to_know(summary)
            + self._contacts(summary)
            + self._footer(summary)
        )
        return self._shell.render(self._css(), meta, body)

    def _personal(self, summary: MedicalSummaryResponse) -> str:
        return (
            "<h2>פרטים אישיים</h2>"
            + self._shell.field("שם", summary.student_name)
            + self._shell.field("ת.ז", summary.national_id)
            + self._shell.field("ת. לידה", self._date(summary))
            + self._shell.field("כתובת", summary.address)
            + self._shell.field("טלפון", summary.phone)
            + self._group("מתגורר ב", "lives_with", summary)
        )

    def _medical(self, summary: MedicalSummaryResponse) -> str:
        return (
            "<h2>מידע ונתונים בריאותיים</h2>"
            + self._texts(summary, _MEDICAL_TEXTS)
            + self._group("טיפולי שיניים / חניכיים", "dental_treatment", summary)
            + self._group("מערכות שיניים", "dentures", summary)
            + self._yes_no("ידוע על אפילפסיה", summary.epilepsy_known)
            + self._shell.field("אופי התקפים", summary.epilepsy_seizure_nature)
            + self._shell.field("תדירות התקפים", summary.epilepsy_seizure_frequency)
            + self._shell.field(
                "התקף אחרון בתאריך",
                (
                    self._shell.value(summary.epilepsy_last_seizure)
                    if summary.epilepsy_last_seizure
                    else ""
                ),
            )
            + self._shell.field("טיפול בזמן התקף", summary.epilepsy_seizure_treatment)
            + self._yes_no("ידוע על תחלואה כפולה", summary.dual_diagnosis_known)
            + self._shell.field("מתבטא ב", summary.dual_diagnosis_expression)
            + self._shell.field("תדירות", summary.dual_diagnosis_frequency)
            + self._shell.field("טיפול שניתן", summary.dual_diagnosis_treatment)
            + self._group("שלמות העור", "skin_integrity", summary)
            + self._shell.field("ידוע על", summary.skin_known_issues)
            + f'<p class="note">{escape(_MEDICATION_NOTE)}</p>'
        )

    def _functioning(self, summary: MedicalSummaryResponse) -> str:
        groups = "".join(self._group(title, group, summary) for group, title in _FUNCTION_GROUPS)
        return (
            "<h2>תפקוד ותקשורת</h2>"
            + groups
            + self._yes_no("האכלה באמצעות גסטרוסטום", summary.gastrostomy_feeding)
            + self._shell.field("פורמולה", summary.formula)
            + "".join(self._group(title, group, summary) for group, title in _NOURISHMENT_GROUPS)
            + self._group("דיאטה", "diet", summary)
            + self._group("שליטה על סוגרים", "continence", summary)
        )

    def _good_to_know(self, summary: MedicalSummaryResponse) -> str:
        return "<h2>חשוב לדעת</h2>" + self._texts(summary, _GOOD_TO_KNOW)

    def _contacts(self, summary: MedicalSummaryResponse) -> str:
        return (
            "<h2>אנשי קשר וגורמים מטפלים</h2>"
            + self._shell.field("שם אפוטרופוס", summary.guardian_name)
            + self._shell.field("קרבה", summary.guardian_relation)
            + self._shell.field("טלפון זמין", summary.guardian_phone)
            + self._shell.field("מבוטח בשירותי בריאות", summary.health_fund)
            + self._yes_no("ביטוח רפואי נוסף", summary.supplemental_insurance)
            + self._shell.field("פירוט ביטוח נוסף", summary.supplemental_insurance_detail)
            + self._shell.field("שם הרופא מנהל הטיפול", summary.attending_doctor)
            + self._shell.field("שם האחות מנהלת טיפול", summary.care_nurse)
            + self._shell.field("עו״ס בקהילה", summary.community_social_worker)
            + self._shell.field("טלפון עו״ס", summary.social_worker_phone)
        )

    def _footer(self, summary: MedicalSummaryResponse) -> str:
        return (
            '<div class="footer">'
            + self._shell.field("שם ממלא הטופס", summary.written_by_name)
            + self._shell.field("תפקידו", summary.filler_role)
            + '<div class="field signature"><span class="label">חתימה: </span>'
            '<span class="signature-line"></span></div>'
            "</div>"
        )

    def _date(self, summary: MedicalSummaryResponse) -> str:
        return self._shell.value(summary.date_of_birth) if summary.date_of_birth else ""

    def _texts(self, summary: MedicalSummaryResponse, sections: tuple[tuple[str, str], ...]) -> str:
        return "".join(
            f"<h3>{escape(title)}</h3>"
            f'<div class="section-body">{self._shell.value(getattr(summary, field))}</div>'
            for field, title in sections
        )

    def _group(self, title: str, group: str, summary: MedicalSummaryResponse) -> str:
        chosen: list[str] = getattr(summary, group)
        detail_value, detail_field = _OTHER_TEXTS.get(group, ("", ""))
        details = {detail_value: getattr(summary, detail_field)} if detail_field else {}
        return self._checklist(title, MEDICAL_SUMMARY_OPTIONS[group], chosen, details)

    def _yes_no(self, title: str, value: bool | None) -> str:
        chosen = [] if value is None else ["yes" if value else "no"]
        return self._checklist(title, _YES_NO, chosen, {})

    def _checklist(
        self,
        title: str,
        options: Sequence[tuple[str, str]],
        chosen: Sequence[str],
        details: dict[str, str],
    ) -> str:
        items = []
        for value, label in options:
            checked = value in chosen
            text = escape(label)
            if checked and details.get(value):
                text += f": {escape(details[value])}"
            box = "box checked" if checked else "box"
            items.append(f'<span class="option"><span class="{box}"></span>{text}</span>')
        return (
            f'<div class="group"><span class="label">{escape(title)}: </span>'
            f'{"".join(items)}</div>'
        )

    def _css(self) -> str:
        return (
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt;"
            "margin-top:16pt}"
            f"h3{{color:{self._brand.primary_color};font-size:11.5pt;margin:10pt 0 2pt}}"
            f".field{{margin:3pt 0}}.label{{color:{self._brand.muted_color}}}"
            ".section-body{white-space:pre-wrap;margin:2pt 0 4pt}"
            ".group{margin:5pt 0;line-height:1.7}"
            ".option{display:inline-block;margin-left:12pt}"
            f".box{{display:inline-block;width:9pt;height:9pt;border:1pt solid "
            f"{self._brand.text_color};margin-left:4pt;vertical-align:middle}}"
            f".box.checked{{background:{self._brand.primary_color};"
            f"border-color:{self._brand.primary_color}}}"
            f".note{{color:{self._brand.muted_color};font-size:9.5pt;margin-top:8pt}}"
            f".footer{{margin-top:24pt;border-top:1px solid {self._brand.muted_color};"
            "padding-top:8pt}"
            ".signature{margin-top:14pt}"
            ".signature-line{display:inline-block;width:5cm;"
            f"border-bottom:1px solid {self._brand.text_color}}}"
        )
