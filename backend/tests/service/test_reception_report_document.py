import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.reception_checklist_item import ReceptionChecklistItem
from backend.app.schema.routes.reception_report_response import ReceptionReportResponse
from backend.app.service.reports.reception_report_document import ReceptionReportDocument


def _report(**overrides: object) -> ReceptionReportResponse:
    base: dict[str, object] = {
        "student_id": uuid.uuid4(),
        "exists": True,
        "student_name": "נועה",
        "national_id": "123456782",
        "date_of_birth": date(2010, 5, 1),
        "committee_date": date(2026, 9, 1),
        "committee_participants": "רכזת",
        "intake_date": date(2026, 9, 10),
        "committee_summary": "סיכום ועדה",
        "committee_recommendations": "המלצות הוועדה",
        "framework_code": "1234",
        "tariff_code": "5678",
        "committee_held": ReceptionChecklistItem(done=True, note="נערכה כנדרש"),
        "director_approval": ReceptionChecklistItem(done=True),
        "family_guardian_housing_updated": ReceptionChecklistItem(done=False),
        "community_social_worker_updated": ReceptionChecklistItem(done=True),
        "management_updated": ReceptionChecklistItem(done=False),
        "written_by_name": "רכזת",
        "updated_at": datetime.now(UTC),
    }
    base.update(overrides)
    return ReceptionReportResponse(**base)


def test_html_is_rtl_and_contains_all_sections() -> None:
    html = ReceptionReportDocument(BrandSettings()).to_html(_report(), "מוסד בדיקה")

    assert 'dir="rtl"' in html
    assert "דוח קבלה" in html
    assert "נועה" in html
    assert "123456782" in html
    assert "סיכום ועדת קבלה" in html
    assert "בקרת תהליך לביצוע נוהל קבלת מקבל שירות" in html
    assert "התקיימה ועדת קבלה על פי הנוהל?" in html
    assert "נערכה כנדרש" in html
    assert "בוצע" in html
    assert "לא בוצע" in html
    assert "נכתב על ידי" in html
    assert "רכזת" in html


def test_html_escapes_free_text() -> None:
    html = ReceptionReportDocument(BrandSettings()).to_html(
        _report(committee_summary="<script>x</script>"), "מוסד בדיקה"
    )

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_values_render_a_dash() -> None:
    html = ReceptionReportDocument(BrandSettings()).to_html(
        _report(committee_recommendations="", written_by_name=None), "מוסד בדיקה"
    )

    assert "—" in html


def test_carries_the_institution_name() -> None:
    html = ReceptionReportDocument(BrandSettings()).to_html(_report(), "בית ספר השרון")

    assert "בית ספר השרון" in html
