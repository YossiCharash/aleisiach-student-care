import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.routes.social_note_entry_response import SocialNoteEntryResponse
from backend.app.schema.routes.social_note_report_response import SocialNoteReportResponse
from backend.app.service.notes.social_note_document import SocialNoteDocument


def _entry(content: str = "שיחה עם ההורים", author_name: str = "מור") -> SocialNoteEntryResponse:
    now = datetime.now(UTC)
    return SocialNoteEntryResponse(
        id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        note_date=date(2026, 8, 30),
        content=content,
        author_id=uuid.uuid4(),
        author_name=author_name,
        created_at=now,
        updated_at=now,
    )


def _report(entries: list[SocialNoteEntryResponse]) -> SocialNoteReportResponse:
    return SocialNoteReportResponse(student_id=uuid.uuid4(), student_name="דנה", entries=entries)


def test_combined_html_is_rtl_and_contains_entries() -> None:
    html = SocialNoteDocument(BrandSettings()).combined_html(_report([_entry()]), "מוסד בדיקה")

    assert 'dir="rtl"' in html
    assert "דנה" in html
    assert "שיחה עם ההורים" in html
    assert "מור" in html
    assert "30/08/2026" in html
    assert "מוסד בדיקה" in html


def test_combined_html_handles_no_entries() -> None:
    html = SocialNoteDocument(BrandSettings()).combined_html(_report([]), "מוסד בדיקה")

    assert "אין סיכומי עו״ס להצגה." in html
    assert "דנה" in html


def test_single_html_renders_one_entry() -> None:
    entry = _entry(content="הערה בודדת")
    html = SocialNoteDocument(BrandSettings()).single_html(_report([entry]), "מוסד בדיקה")

    assert "הערה בודדת" in html
    assert "סיכום עו״ס" in html


def test_html_escapes_note_content() -> None:
    html = SocialNoteDocument(BrandSettings()).combined_html(
        _report([_entry(content="<script>x</script>")]), "מוסד בדיקה"
    )

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_headings_use_the_primary_brand_green() -> None:
    html = SocialNoteDocument(BrandSettings()).combined_html(_report([_entry()]), "מוסד בדיקה")

    assert "h1{color:#3F8420" in html
