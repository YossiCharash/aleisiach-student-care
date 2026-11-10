import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.medical_summary_entry_response import MedicalSummaryEntryResponse
from backend.app.schema.routes.medical_summary_history_response import (
    MedicalSummaryHistoryResponse,
)
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.medical_summary_document import MedicalSummaryDocument


def _issue(institution_name: str = "מוסד בדיקה") -> IssueContext:
    return IssueContext(
        institution_name=institution_name,
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 11, 10),
    )


def _entry(**overrides: object) -> MedicalSummaryEntryResponse:
    now = datetime(2026, 11, 10, tzinfo=UTC)
    base: dict[str, object] = {
        "id": uuid.uuid4(),
        "student_id": uuid.uuid4(),
        "summary_date": date(2026, 11, 1),
        "author_id": uuid.uuid4(),
        "author_name": "מנהלת",
        "created_at": now,
        "updated_at": now,
        "allergies": "בוטנים",
        "mobility": ["escort"],
        "diet": ["other"],
        "diet_other": "ללא גלוטן",
        "epilepsy_known": False,
        "filler_role": "אחות",
    }
    base.update(overrides)
    return MedicalSummaryEntryResponse.model_validate(base)


def _history(*entries: MedicalSummaryEntryResponse) -> MedicalSummaryHistoryResponse:
    return MedicalSummaryHistoryResponse(
        student_id=uuid.uuid4(),
        student_name="נועה כהן",
        national_id="123456782",
        date_of_birth=date(2000, 5, 1),
        address="רחוב הגפן 3",
        entries=list(entries),
    )


def _html(**overrides: object) -> str:
    return MedicalSummaryDocument(BrandSettings()).single_html(
        _history(_entry(**overrides)), _issue()
    )


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
    html = MedicalSummaryDocument(BrandSettings()).single_html(
        _history(_entry()), _issue("בית ספר השרון")
    )

    assert "בית ספר השרון" in html


def test_communication_detail_shows_only_beside_a_ticked_alternative() -> None:
    ticked = _html(communication=["alternative"], communication_other="לוח תקשורת")
    unticked = _html(communication=["independent"], communication_other="לוח תקשורת")

    assert "מתקשר בתקשורת חליפית (פלט / לוח / אחר): לוח תקשורת" in ticked
    assert "לוח תקשורת" not in unticked


def test_combined_lists_every_entry_under_its_date() -> None:
    history = _history(
        _entry(summary_date=date(2026, 6, 1), allergies="חלב"),
        _entry(summary_date=date(2026, 1, 1), allergies="ביצים"),
    )

    html = MedicalSummaryDocument(BrandSettings()).combined_html(history, _issue())

    assert "כל התאריכים" in html
    assert html.index("01/06/2026") < html.index("01/01/2026")
    assert "חלב" in html
    assert "ביצים" in html
    assert html.count('class="entry"') == 2


def test_combined_without_entries_says_so() -> None:
    html = MedicalSummaryDocument(BrandSettings()).combined_html(_history(), _issue())

    assert "אין סיכומי מידע רפואי להצגה" in html
