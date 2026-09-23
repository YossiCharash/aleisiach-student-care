import uuid
from datetime import date

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.supported_employment_response import SupportedEmploymentResponse
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.supported_employment_document import (
    SupportedEmploymentDocument,
)


def _issue(institution_name: str = "מוסד בדיקה") -> IssueContext:
    return IssueContext(
        institution_name=institution_name,
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 9, 23),
    )


def _report(**overrides: object) -> SupportedEmploymentResponse:
    base: dict[str, object] = {
        "student_id": uuid.uuid4(),
        "exists": True,
        "workplace": "מאפייה מרכזית",
        "address": "רחוב הפרחים 5",
        "activity_type": "אריזה",
        "work_process": "אריזת מאפים",
        "work_environment": "מטבח תעשייתי",
        "required_body_functions": "עמידה ממושכת",
        "hazards_and_safety": "תנור חם",
        "workplace_contact": "דנה",
        "escort_contact": "יוסי",
        "mobility": "הסעה מאורגנת",
        "work_hours": "08:00-14:00",
    }
    base.update(overrides)
    return SupportedEmploymentResponse(**base)


def test_html_is_rtl_and_contains_all_fields() -> None:
    html = SupportedEmploymentDocument(BrandSettings()).to_html(_report(), _issue())

    assert 'dir="rtl"' in html
    assert "ניתוח עבודה נתמכת" in html
    assert "מקום העבודה" in html
    assert "מאפייה מרכזית" in html
    assert "סכנות ובטיחות" in html
    assert "תנור חם" in html
    assert "שעת עבודה" in html
    assert "08:00-14:00" in html


def test_html_escapes_free_text() -> None:
    html = SupportedEmploymentDocument(BrandSettings()).to_html(
        _report(work_process="<script>x</script>"), _issue()
    )

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_value_renders_a_dash() -> None:
    html = SupportedEmploymentDocument(BrandSettings()).to_html(_report(mobility=""), _issue())

    assert "—" in html


def test_carries_the_institution_name() -> None:
    html = SupportedEmploymentDocument(BrandSettings()).to_html(_report(), _issue("בית ספר השרון"))

    assert "בית ספר השרון" in html
