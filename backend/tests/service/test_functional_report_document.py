import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.functional_report_response import FunctionalReportResponse
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.functional_report_document import FunctionalReportDocument


def _issue(institution_name: str = "מוסד בדיקה") -> IssueContext:
    return IssueContext(
        institution_name=institution_name,
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 9, 23),
    )


def _report(**overrides: object) -> FunctionalReportResponse:
    base: dict[str, object] = {
        "student_id": uuid.uuid4(),
        "exists": True,
        "student_name": "נועה",
        "national_id": "123456782",
        "date_of_birth": date(2010, 5, 1),
        "general_background": "רקע כללי",
        "vocational_domain": "תחום תעסוקתי",
        "behavioral_emotional_domain": "תחום רגשי",
        "communication_social_domain": "תחום תקשורתי",
        "independence_life_skills_domain": "עצמאות",
        "summary_recommendations": "סיכום והמלצות",
        "written_by_name": "רכזת",
        "updated_at": datetime.now(UTC),
    }
    base.update(overrides)
    return FunctionalReportResponse(**base)


def test_html_is_rtl_and_contains_all_sections() -> None:
    html = FunctionalReportDocument(BrandSettings()).to_html(_report(), _issue())

    assert 'dir="rtl"' in html
    assert "דוח תפקודי" in html
    assert "נועה" in html
    assert "123456782" in html
    assert "רקע כללי" in html
    assert "התחום התעסוקתי" in html
    assert "תחום עצמאות וכישורי חיים" in html
    assert "נכתב על ידי" in html
    assert "רכזת" in html


def test_html_escapes_section_text() -> None:
    html = FunctionalReportDocument(BrandSettings()).to_html(
        _report(general_background="<script>x</script>"), _issue()
    )

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_sections_render_a_dash() -> None:
    html = FunctionalReportDocument(BrandSettings()).to_html(
        _report(vocational_domain="", written_by_name=None), _issue()
    )

    assert "—" in html


def test_carries_the_institution_name() -> None:
    html = FunctionalReportDocument(BrandSettings()).to_html(_report(), _issue("בית ספר השרון"))

    assert "בית ספר השרון" in html


def test_issue_metadata_appears_in_the_header_card() -> None:
    html = FunctionalReportDocument(BrandSettings()).to_html(_report(), _issue())

    assert "הופק על ידי" in html
    assert "מפיקה" in html
    assert "תאריך הנפקה" in html
    assert "23/09/2026" in html
