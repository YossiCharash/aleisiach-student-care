from html import escape

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.student_details_response import StudentDetailsResponse

_LEGAL_STATUS_LABELS = {
    LegalStatus.GUARDIAN_APPOINTED: "מונה אפוטרופוס",
    LegalStatus.PARENTS_ARE_GUARDIANS: "הורים אפוטרופסים",
}
_IDD_NAME = "מגבלה שכלית התפתחותית"

_CSS = (
    "body{font-family:'Heebo',sans-serif;direction:rtl;color:#333333;margin:2cm}"
    "h1{color:#CC3366;font-size:20pt}"
    "h2{color:#85C441;font-size:14pt;border-bottom:2px solid #85C441;padding-bottom:2pt}"
    ".institution{color:#5C5C5C;font-size:11pt;margin:0}"
    ".field{margin:3pt 0}.label{color:#5C5C5C}ul{margin:0;padding-inline-start:18pt}"
)


class StudentDetailsDocument:
    def to_html(self, details: StudentDetailsResponse, institution_name: str) -> str:
        sections = [
            self._identity(details),
            self._diagnoses(details),
            self._contacts("אנשי קשר לחירום", details.emergency_contacts),
        ]
        if details.sensitive_visible:
            sections.append(self._guardianship(details))
        sections.append(self._medical_profile(details))
        sections.append(self._communication(details))
        sections.append(self._background(details))
        sections.append(self._emotional_id(details))
        body = "".join(sections)
        return (
            '<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">'
            f"<style>{_CSS}</style></head><body>"
            f'<p class="institution">{escape(institution_name)}</p>'
            f"<h1>פרטי תלמיד</h1>{body}</body></html>"
        )

    def _identity(self, details: StudentDetailsResponse) -> str:
        age = str(details.age) if details.age is not None else "—"
        dob = details.date_of_birth.isoformat() if details.date_of_birth is not None else "—"
        fields = [
            self._field("תעודת זהות", details.national_id),
            self._field("תאריך לידה", dob),
            self._field("גיל", age),
            self._field("כתובת", details.address),
            self._field("שפת דיבור עיקרית בבית", details.home_language),
        ]
        return "<h2>זהות</h2>" + "".join(fields)

    def _diagnoses(self, details: StudentDetailsResponse) -> str:
        severity = details.idd_severity if details.idd_severity else "—"
        items = [f"<li>{escape(_IDD_NAME)} — דרגה: {escape(severity)}</li>"]
        items.extend(f"<li>{escape(name)}</li>" for name in details.additional_diagnoses)
        return f"<h2>אבחונים</h2><ul>{''.join(items)}</ul>"

    def _medical_profile(self, details: StudentDetailsResponse) -> str:
        allergies = self._list_or_dash(
            details.allergies_dietary if details.has_allergies_or_dietary else []
        )
        medications = self._list_or_dash(
            details.medications if details.takes_regular_medication else []
        )
        independence = (
            details.medication_independence
            if details.takes_regular_medication and details.medication_independence
            else "—"
        )
        devices = self._device_labels(details)
        return (
            "<h2>פרופיל רפואי ובטיחותי קריטי</h2>"
            + self._block("אלרגיות / מגבלות תזונה", allergies)
            + self._block("תרופות קבועות", medications)
            + self._field("מידת עצמאות בלקיחת תרופות", independence)
            + self._field("פרוטוקול חירום רפואי", details.emergency_protocol)
            + self._block("אביזרי עזר פיזיים", devices)
        )

    def _block(self, label: str, body: str) -> str:
        return f"<div class='field'><span class='label'>{escape(label)}:</span></div>{body}"

    def _communication(self, details: StudentDetailsResponse) -> str:
        return (
            "<h2>ערוץ תקשורת מועדף</h2>"
            + self._field("אופן הבעה עיקרי", details.expression_mode)
            + self._field("מידת הבנת השפה", details.language_comprehension)
        )

    def _background(self, details: StudentDetailsResponse) -> str:
        return (
            "<h2>רקע חינוכי ותעסוקתי קודם</h2>"
            + self._field("מסגרת נוכחית או אחרונה", details.current_or_last_framework)
            + self._field("ניסיון קודם במטלות / עבודות", details.prior_task_experience)
        )

    def _emotional_id(self, details: StudentDetailsResponse) -> str:
        return (
            "<h2>תעודת זהות רגשית</h2>"
            + self._field("תחומי עניין וחוזקות", details.interests_strengths)
            + self._field("גורמים מציפים / טריגרים", details.triggers)
            + self._field("סימנים מקדימים למצוקה", details.distress_early_signs)
            + self._field("דרכי הרגעה מומלצות", details.calming_methods)
        )

    def _device_labels(self, details: StudentDetailsResponse) -> str:
        labels = list(details.assistive_devices)
        if details.assistive_device_other:
            labels.append(f"אחר: {details.assistive_device_other}")
        return self._list_or_dash(labels)

    def _list_or_dash(self, values: list[str]) -> str:
        if not values:
            return self._field("", "—")
        items = "".join(f"<li>{escape(value)}</li>" for value in values)
        return f"<ul>{items}</ul>"

    def _contacts(self, title: str, contacts: list[ContactInfo]) -> str:
        if not contacts:
            return f"<h2>{escape(title)}</h2>" + self._field("", "—")
        items = "".join(f"<li>{self._contact_line(contact)}</li>" for contact in contacts)
        return f"<h2>{escape(title)}</h2><ul>{items}</ul>"

    def _guardianship(self, details: StudentDetailsResponse) -> str:
        status = (
            _LEGAL_STATUS_LABELS[details.legal_status] if details.legal_status is not None else "—"
        )
        head = "<h2>אפוטרופסות ומעמד משפטי</h2>" + self._field("מעמד משפטי", status)
        if not details.guardians:
            return head + self._field("אפוטרופסים", "—")
        items = "".join(
            f"<li>{self._contact_line(guardian)}</li>" for guardian in details.guardians
        )
        return head + f"<ul>{items}</ul>"

    def _contact_line(self, contact: ContactInfo) -> str:
        parts = [escape(contact.full_name)]
        if contact.relationship:
            parts.append(f"({escape(contact.relationship)})")
        if contact.phone:
            parts.append(escape(contact.phone))
        return " ".join(parts)

    def _field(self, label: str, value: str | None) -> str:
        shown = escape(value) if value else "—"
        prefix = f'<span class="label">{escape(label)}: </span>' if label else ""
        return f'<div class="field">{prefix}{shown}</div>'
