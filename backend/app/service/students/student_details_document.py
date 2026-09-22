from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.student_details_response import StudentDetailsResponse
from backend.app.utils.service.document_shell import DocumentShell

_LEGAL_STATUS_LABELS = {
    LegalStatus.GUARDIAN_APPOINTED: "מונה אפוטרופוס",
    LegalStatus.PARENTS_ARE_GUARDIANS: "הורים אפוטרופסים",
}
_IDD_NAME = "מגבלה שכלית התפתחותית"


class StudentDetailsDocument:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._shell = DocumentShell(brand)

    def _css(self) -> str:
        return (
            f"h2{{color:{self._brand.accent_color};font-size:14pt;"
            f"border-bottom:2px solid {self._brand.accent_color};padding-bottom:2pt}}"
            f".field{{margin:3pt 0}}.label{{color:{self._brand.muted_color}}}"
            "ul{margin:0;padding-inline-start:18pt}"
        )

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
        return self._shell.render(self._css(), institution_name, "פרטי חניך", body)

    def _identity(self, details: StudentDetailsResponse) -> str:
        dob = details.date_of_birth.isoformat() if details.date_of_birth is not None else None
        age = str(details.age) if details.age is not None else None
        return self._section(
            "זהות",
            self._field("תעודת זהות", details.national_id),
            self._field("תאריך לידה", dob),
            self._field("גיל", age),
            self._field("כתובת", details.address),
            self._field("שפת דיבור עיקרית בבית", details.home_language),
        )

    def _diagnoses(self, details: StudentDetailsResponse) -> str:
        severity = details.idd_severity
        head = escape(_IDD_NAME) + (f" — דרגה: {escape(severity)}" if severity else "")
        items = [f"<li>{head}</li>"]
        for entry in details.additional_diagnoses:
            text = escape(entry.name)
            if entry.note:
                text += f" — {escape(entry.note)}"
            items.append(f"<li>{text}</li>")
        return self._section(
            "אבחונים",
            f"<ul>{''.join(items)}</ul>",
            self._field("אוטיזם", details.functioning_level),
        )

    def _medical_profile(self, details: StudentDetailsResponse) -> str:
        allergies = list(details.allergies_dietary) if details.has_allergies_or_dietary else []
        medications = list(details.medications) if details.takes_regular_medication else []
        independence = details.medication_independence if details.takes_regular_medication else None
        return self._section(
            "פרופיל רפואי ובטיחותי קריטי",
            self._named_list("אלרגיות / מגבלות תזונה", allergies),
            self._named_list("תרופות קבועות", medications),
            self._field("מידת עצמאות בלקיחת תרופות", independence),
            self._field("פרוטוקול חירום רפואי", details.emergency_protocol),
            self._named_list("אביזרי עזר פיזיים", self._device_labels(details)),
        )

    def _communication(self, details: StudentDetailsResponse) -> str:
        return self._section(
            "ערוץ תקשורת מועדף",
            self._field("אופן הבעה עיקרי", details.expression_mode),
            self._field("מידת הבנת השפה", details.language_comprehension),
        )

    def _background(self, details: StudentDetailsResponse) -> str:
        return self._section(
            "רקע חינוכי ותעסוקתי קודם",
            self._field("מוסד קודם", details.previous_institution),
            self._field("רקע תעסוקתי קודם", details.prior_task_experience),
        )

    def _emotional_id(self, details: StudentDetailsResponse) -> str:
        return self._section(
            "תעודת זהות רגשית",
            self._field("תחומי עניין וחוזקות", details.interests_strengths),
            self._field("גורמים מציפים / טריגרים", details.triggers),
            self._field("סימנים מקדימים למצוקה", details.distress_early_signs),
            self._field("דרכי הרגעה מומלצות", details.calming_methods),
        )

    def _contacts(self, title: str, contacts: list[ContactInfo]) -> str:
        if not contacts:
            return ""
        items = "".join(f"<li>{self._contact_line(contact)}</li>" for contact in contacts)
        return f"<h2>{escape(title)}</h2><ul>{items}</ul>"

    def _guardianship(self, details: StudentDetailsResponse) -> str:
        status = (
            _LEGAL_STATUS_LABELS[details.legal_status] if details.legal_status is not None else None
        )
        parts = [self._field("מעמד משפטי", status)]
        if details.guardians:
            items = "".join(
                f"<li>{self._contact_line(guardian)}</li>" for guardian in details.guardians
            )
            parts.append(f"<ul>{items}</ul>")
        return self._section("אפוטרופסות ומעמד משפטי", *parts)

    def _device_labels(self, details: StudentDetailsResponse) -> list[str]:
        labels = list(details.assistive_devices)
        if details.assistive_device_other:
            labels.append(f"אחר: {details.assistive_device_other}")
        return labels

    def _contact_line(self, contact: ContactInfo) -> str:
        parts = [escape(contact.full_name)]
        if contact.relationship:
            parts.append(f"({escape(contact.relationship)})")
        if contact.phone:
            parts.append(escape(contact.phone))
        return " ".join(parts)

    def _section(self, title: str, *parts: str) -> str:
        body = "".join(part for part in parts if part)
        return f"<h2>{escape(title)}</h2>{body}" if body else ""

    def _field(self, label: str, value: str | None) -> str:
        if value is None or not value.strip():
            return ""
        return (
            f'<div class="field"><span class="label">{escape(label)}: </span>'
            f"{escape(value)}</div>"
        )

    def _named_list(self, label: str, values: list[str]) -> str:
        if not values:
            return ""
        items = "".join(f"<li>{escape(value)}</li>" for value in values)
        return (
            f'<div class="field"><span class="label">{escape(label)}:</span></div>'
            f"<ul>{items}</ul>"
        )
