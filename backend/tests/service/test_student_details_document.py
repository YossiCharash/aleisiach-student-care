import uuid
from datetime import date

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis
from backend.app.schema.routes.student_details_response import StudentDetailsResponse
from backend.app.service.students.student_details_document import StudentDetailsDocument


def _details(
    national_id: str = "123456789", sensitive_visible: bool = True
) -> StudentDetailsResponse:
    return StudentDetailsResponse(
        student_id=uuid.uuid4(),
        national_id=national_id,
        date_of_birth=date(2012, 5, 1),
        age=14,
        address="רחוב הבנים 1",
        home_language="עברית",
        medical_diagnoses=[Diagnosis(name="ADHD", notes="קל")],
        emergency_contacts=[ContactInfo(full_name="אמא", phone="050")],
        legal_status=LegalStatus.GUARDIAN_APPOINTED,
        guardians=[ContactInfo(full_name="דוד", relationship="דוד")],
        sensitive_visible=sensitive_visible,
    )


def test_full_details_include_guardianship() -> None:
    html = StudentDetailsDocument().to_html(_details())

    assert 'dir="rtl"' in html
    assert "123456789" in html
    assert "ADHD" in html
    assert "אמא" in html
    assert "אפוטרופסות ומעמד משפטי" in html
    assert "מונה אפוטרופוס" in html
    assert "דוד" in html


def test_redacted_details_omit_guardianship() -> None:
    html = StudentDetailsDocument().to_html(_details(sensitive_visible=False))

    assert "אפוטרופסות ומעמד משפטי" not in html
    assert "מונה אפוטרופוס" not in html
    assert "ADHD" in html
    assert "אמא" in html


def test_details_html_escapes_content() -> None:
    html = StudentDetailsDocument().to_html(_details(national_id="<b>x</b>"))

    assert "<b>x</b>" not in html
    assert "&lt;b&gt;" in html
