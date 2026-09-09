import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.schema.routes.plan_entry_response import PlanEntryResponse
from backend.app.schema.routes.plan_solution_response import PlanSolutionResponse
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_strength import ProgramStrength
from backend.app.service.meetings.meeting_summary_document import MeetingSummaryDocument


def _meeting(area_name: str = "רחיצת ידיים", summary: str = "סיכום הישיבה") -> MeetingResponse:
    now = datetime.now(UTC)
    return MeetingResponse(
        id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        meeting_date=date(2026, 8, 15),
        summary=summary,
        created_at=now,
        updated_at=now,
        strengths=[ProgramStrength(skill_id=uuid.uuid4(), skill_name="הבעה")],
        areas_to_strengthen=[
            ProgramArea(skill_id=uuid.uuid4(), skill_name=area_name, rating=MeetingRating.YELLOW)
        ],
        plan_entries=[
            PlanEntryResponse(
                skill_id=uuid.uuid4(),
                skill_name_snapshot=area_name,
                rating=MeetingRating.YELLOW,
                solutions=[
                    PlanSolutionResponse(
                        solution_id=uuid.uuid4(),
                        solution_text_snapshot="תרגול יומי",
                    )
                ],
            )
        ],
    )


def test_html_is_rtl_and_contains_content() -> None:
    html = MeetingSummaryDocument(BrandSettings()).to_html(_meeting(), "מוסד בדיקה")

    assert 'dir="rtl"' in html
    assert "הבעה" in html
    assert "רחיצת ידיים" in html
    assert "בהשגחה" in html
    assert "תרגול יומי" in html
    assert "15/08/2026" in html
    assert "סיכום הישיבה" in html


def test_html_escapes_snapshot_text() -> None:
    html = MeetingSummaryDocument(BrandSettings()).to_html(
        _meeting(area_name="<script>x</script>"), "מוסד בדיקה"
    )

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_summary_html_carries_the_institution_name() -> None:
    html = MeetingSummaryDocument(BrandSettings()).to_html(_meeting(), "בית ספר השרון")

    assert "בית ספר השרון" in html


def test_headings_use_the_primary_brand_green() -> None:
    html = MeetingSummaryDocument(BrandSettings()).to_html(_meeting(), "מוסד בדיקה")

    assert "h1{color:#3F8420" in html


def test_table_header_puts_white_text_on_the_primary_green() -> None:
    html = MeetingSummaryDocument(BrandSettings()).to_html(_meeting(), "מוסד בדיקה")

    assert "th{background:#3F8420;color:#ffffff}" in html
