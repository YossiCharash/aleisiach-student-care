import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.functional_report_entry_response import (
    FunctionalReportEntryResponse,
)
from backend.app.schema.routes.functional_report_history_response import (
    FunctionalReportHistoryResponse,
)
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.functional_report_document import FunctionalReportDocument


def _issue(institution_name: str = "מוסד בדיקה") -> IssueContext:
    return IssueContext(
        institution_name=institution_name,
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 9, 23),
    )


def _entry(**overrides: object) -> FunctionalReportEntryResponse:
    now = datetime.now(UTC)
    base: dict[str, object] = {
        "id": uuid.uuid4(),
        "student_id": uuid.uuid4(),
        "report_date": date(2026, 9, 1),
        "general_background": "רקע כללי",
        "vocational_domain": "תחום תעסוקתי",
        "behavioral_emotional_domain": "תחום רגשי",
        "communication_social_domain": "תחום תקשורתי",
        "independence_life_skills_domain": "עצמאות",
        "summary_recommendations": "סיכום והמלצות",
        "author_id": uuid.uuid4(),
        "author_name": "רכזת",
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return FunctionalReportEntryResponse.model_validate(base)


def _history(*entries: FunctionalReportEntryResponse) -> FunctionalReportHistoryResponse:
    return FunctionalReportHistoryResponse(
        student_id=uuid.uuid4(),
        student_name="נועה",
        national_id="123456782",
        date_of_birth=date(2010, 5, 1),
        entries=list(entries),
    )


def _document() -> FunctionalReportDocument:
    return FunctionalReportDocument(BrandSettings())


def test_single_html_is_rtl_and_contains_all_sections() -> None:
    html = _document().single_html(_history(_entry()), _issue())

    assert 'dir="rtl"' in html
    assert "דוח תפקודי" in html
    assert "נועה" in html
    assert "123456782" in html
    assert "רקע כללי" in html
    assert "התחום התעסוקתי" in html
    assert "תחום עצמאות וכישורי חיים" in html
    assert "נכתב על ידי" in html
    assert "רכזת" in html


def test_single_html_shows_the_report_date() -> None:
    html = _document().single_html(_history(_entry()), _issue())

    assert "01/09/2026" in html


def test_combined_html_lists_every_dated_entry_newest_first() -> None:
    html = _document().combined_html(
        _history(
            _entry(report_date=date(2026, 9, 1), general_background="חדש"),
            _entry(report_date=date(2026, 1, 1), general_background="ישן"),
        ),
        _issue(),
    )

    assert "כל התאריכים" in html
    assert "01/09/2026" in html
    assert "01/01/2026" in html
    assert html.index("חדש") < html.index("ישן")


def test_combined_html_without_entries_says_so() -> None:
    html = _document().combined_html(_history(), _issue())

    assert "אין דוחות תפקודיים להצגה" in html


def test_html_escapes_section_text() -> None:
    html = _document().single_html(
        _history(_entry(general_background="<script>x</script>")), _issue()
    )

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_sections_render_a_dash() -> None:
    html = _document().single_html(
        _history(_entry(vocational_domain="", author_name=None)), _issue()
    )

    assert "—" in html


def test_issue_metadata_appears_in_the_header_card() -> None:
    html = _document().single_html(_history(_entry()), _issue("בית ספר השרון"))

    assert "בית ספר השרון" in html
    assert "הופק על ידי" in html
    assert "מפיקה" in html
    assert "23/09/2026" in html
