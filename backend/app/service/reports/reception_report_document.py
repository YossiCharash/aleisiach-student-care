from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.reception_checklist_item import ReceptionChecklistItem
from backend.app.schema.routes.reception_report_response import ReceptionReportResponse
from backend.app.utils.service.document_shell import DocumentShell

_DETAIL_ROWS = (
    ("student_name", "שם העובד/ת"),
    ("national_id", "מספר זהות"),
    ("date_of_birth", "תאריך לידה"),
    ("committee_date", "תאריך ועדת קבלה"),
    ("committee_participants", "משתתפי ועדת קבלה"),
    ("intake_date", "תאריך קליטה"),
    ("committee_summary", "סיכום ועדת קבלה"),
    ("committee_recommendations", "המלצות הוועדה"),
    ("framework_code", "סמל מסגרת"),
    ("tariff_code", "סמל תעריף"),
)
_CHECKLIST_ROWS = (
    ("committee_held", "התקיימה ועדת קבלה על פי הנוהל?"),
    ("director_approval", "התקבל אישור של המנהלת לקליטה?"),
    ("family_guardian_housing_updated", "המשפחה/האפוטרופוס/דיור עודכנו?"),
    ("community_social_worker_updated", "העו״ס בקהילה עודכנה?"),
    ("management_updated", "ההנהלה עודכנה?"),
)


class ReceptionReportDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def _css(self) -> str:
        return (
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt;"
            "margin-top:16pt}"
            "table{width:100%;border-collapse:collapse;margin:8pt 0}"
            f"th,td{{border:1px solid {self._brand.muted_color};padding:5pt;"
            "text-align:right;vertical-align:top;font-size:11pt}"
            f"th{{background:{self._brand.primary_color};color:#ffffff;width:35%;"
            "white-space:nowrap}"
            ".cell{white-space:pre-wrap}"
            f".footer{{margin-top:24pt;border-top:1px solid {self._brand.muted_color};"
            "padding-top:8pt}"
            f".field{{margin:3pt 0}}.label{{color:{self._brand.muted_color}}}"
        )

    def to_html(self, report: ReceptionReportResponse, institution_name: str) -> str:
        body = (
            "<h2>פרטי קליטה</h2>"
            + self._details_table(report)
            + "<h2>בקרת תהליך לביצוע נוהל קבלת מקבל שירות</h2>"
            + self._checklist_table(report)
            + self._footer(report)
        )
        return self._shell.render(self._css(), institution_name, "דוח קבלה", body)

    def _details_table(self, report: ReceptionReportResponse) -> str:
        rows = "".join(
            f"<tr><th>{escape(title)}</th>"
            f'<td class="cell">{self._shell.value(getattr(report, field))}</td></tr>'
            for field, title in _DETAIL_ROWS
        )
        return f"<table>{rows}</table>"

    def _checklist_table(self, report: ReceptionReportResponse) -> str:
        header = "<tr><th>הסעיף בנוהל</th><th>אישור ביצוע</th><th>הערה</th></tr>"
        rows = ""
        for field, title in _CHECKLIST_ROWS:
            item: ReceptionChecklistItem = getattr(report, field)
            mark = "בוצע" if item.done else "לא בוצע"
            rows += (
                f"<tr><td>{escape(title)}</td><td>{mark}</td>"
                f'<td class="cell">{self._shell.value(item.note)}</td></tr>'
            )
        return f"<table>{header}{rows}</table>"

    def _footer(self, report: ReceptionReportResponse) -> str:
        return (
            '<div class="footer">'
            + self._shell.field("נכתב על ידי", report.written_by_name)
            + "</div>"
        )
