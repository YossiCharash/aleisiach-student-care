from html import escape

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis
from backend.app.schema.routes.student_details_response import StudentDetailsResponse

_LEGAL_STATUS_LABELS = {
    LegalStatus.GUARDIAN_APPOINTED: "מונה אפוטרופוס",
    LegalStatus.PARENTS_ARE_GUARDIANS: "הורים אפוטרופסים",
}

_CSS = (
    "body{font-family:'Heebo',sans-serif;direction:rtl;color:#333333;margin:2cm}"
    "h1{color:#CC3366;font-size:20pt}"
    "h2{color:#85C441;font-size:14pt;border-bottom:2px solid #85C441;padding-bottom:2pt}"
    ".field{margin:3pt 0}.label{color:#5C5C5C}ul{margin:0;padding-inline-start:18pt}"
)


class StudentDetailsDocument:
    def to_html(self, details: StudentDetailsResponse) -> str:
        sections = [
            self._identity(details),
            self._diagnoses(details.medical_diagnoses),
            self._contacts("אנשי קשר לחירום", details.emergency_contacts),
        ]
        if details.sensitive_visible:
            sections.append(self._guardianship(details))
        body = "".join(sections)
        return (
            '<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">'
            f"<style>{_CSS}</style></head><body><h1>פרטי תלמיד</h1>{body}</body></html>"
        )

    def _identity(self, details: StudentDetailsResponse) -> str:
        age = str(details.age) if details.age is not None else "—"
        dob = details.date_of_birth.isoformat() if details.date_of_birth is not None else "—"
        fields = [
            self._field("תעודת זהות", details.national_id),
            self._field("תאריך לידה", dob),
            self._field("גיל", age),
            self._field("כתובת", details.address),
            self._field("שפת בית", details.home_language),
        ]
        return "<h2>זהות</h2>" + "".join(fields)

    def _diagnoses(self, diagnoses: list[Diagnosis]) -> str:
        if not diagnoses:
            return "<h2>אבחונים</h2>" + self._field("", "—")
        items = "".join(
            f"<li>{escape(item.name)}"
            + (f" — {escape(item.notes)}" if item.notes else "")
            + "</li>"
            for item in diagnoses
        )
        return f"<h2>אבחונים</h2><ul>{items}</ul>"

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
