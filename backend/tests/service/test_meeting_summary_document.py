import uuid
from datetime import UTC, datetime

from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.meeting_entry_response import MeetingEntryResponse
from backend.app.schema.routes.meeting_entry_solution_response import (
    MeetingEntrySolutionResponse,
)
from backend.app.schema.routes.meeting_response import MeetingResponse
from backend.app.service.meetings.meeting_summary_document import MeetingSummaryDocument


def _meeting(skill_name: str = "רחיצת ידיים") -> MeetingResponse:
    return MeetingResponse(
        id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        year=2026,
        month=8,
        author_id=uuid.uuid4(),
        created_at=datetime.now(UTC),
        entries=[
            MeetingEntryResponse(
                id=uuid.uuid4(),
                skill_id=uuid.uuid4(),
                skill_name_snapshot=skill_name,
                rating=MeetingRating.YELLOW,
                solutions=[
                    MeetingEntrySolutionResponse(
                        id=uuid.uuid4(),
                        solution_id=uuid.uuid4(),
                        solution_text_snapshot="תרגול יומי",
                    )
                ],
            )
        ],
    )


def test_html_is_rtl_and_contains_content() -> None:
    html = MeetingSummaryDocument().to_html(_meeting(), "מוסד בדיקה")

    assert 'dir="rtl"' in html
    assert "רחיצת ידיים" in html
    assert "בפיקוח" in html
    assert "תרגול יומי" in html
    assert "08/2026" in html


def test_html_escapes_snapshot_text() -> None:
    html = MeetingSummaryDocument().to_html(_meeting(skill_name="<script>x</script>"), "מוסד בדיקה")

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_summary_html_carries_the_institution_name() -> None:
    html = MeetingSummaryDocument().to_html(_meeting(), "בית ספר השרון")

    assert "בית ספר השרון" in html


def test_headings_use_the_primary_brand_green() -> None:
    html = MeetingSummaryDocument().to_html(_meeting(), "מוסד בדיקה")

    assert "h1{color:#3F8420" in html
