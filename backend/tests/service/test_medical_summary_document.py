import uuid
from datetime import date

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.medical_summary_response import MedicalSummaryResponse
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.medical_summary_document import MedicalSummaryDocument


def _issue(institution_name: str = "מוסד בדיקה") -> IssueContext:
    return IssueContext(
        institution_name=institution_name,
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 11, 10),
    )


def _summary(**overrides: object) -> MedicalSummaryResponse:
    base: dict[str, object] = {
        "student_id": uuid.uuid4(),
        "exists": True,
        "student_name": "נועה כהן",
        "national_id": "123456782",
        "date_of_birth": date(2000, 5, 1),
        "address": "רחוב הגפן 3",
        "allergies": "בוטנים",
        "mobility": ["escort"],
        "diet": ["other"],
        "diet_other": "ללא גלוטן",
        "epilepsy_known": False,
        "written_by_name": "מנהלת",
        "filler_role": "אחות",
    }
    base.update(overrides)
    return MedicalSummaryResponse.model_validate(base)


def _html(**overrides: object) -> str:
    return MedicalSummaryDocument(BrandSettings()).to_html(_summary(**overrides), _issue())


def test_html_is_rtl_with_identity_and_sections() -> None:
    html = _html()

    assert 'dir="rtl"' in html
    assert "סיכום מידע רפואי" in html
    assert "נועה כהן" in html
    assert "123456782" in html
    assert "01/05/2000" in html
    assert "רחוב הגפן 3" in html
    assert "רגישויות / אלרגיה ידועה" in html
    assert "בוטנים" in html
    assert "חשוב לדעת" in html
    assert "מנהלת" in html
    assert "signature-line" in html


def test_checked_options_are_marked() -> None:
    html = _html()

    assert '<span class="box checked"></span>זקוק לליווי' in html
    assert '<span class="box"></span>עצמאי' in html
    assert "אחר: ללא גלוטן" in html
    assert '<span class="box checked"></span>לא' in html


def test_html_escapes_free_text() -> None:
    html = _html(loves="<script>x</script>")

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_carries_the_institution_name() -> None:
    html = MedicalSummaryDocument(BrandSettings()).to_html(_summary(), _issue("בית ספר השרון"))

    assert "בית ספר השרון" in html


def test_communication_detail_shows_only_beside_a_ticked_alternative() -> None:
    ticked = _html(communication=["alternative"], communication_other="לוח תקשורת")
    unticked = _html(communication=["independent"], communication_other="לוח תקשורת")

    assert "מתקשר בתקשורת חליפית (פלט / לוח / אחר): לוח תקשורת" in ticked
    assert "לוח תקשורת" not in unticked
