import uuid
from datetime import date

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.schema.routes.program_strength import ProgramStrength
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.program.foci_document import FociDocument


def _issue() -> IssueContext:
    return IssueContext(
        institution_name="מוסד בדיקה",
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 11, 4),
    )


def _program(
    strengths: list[ProgramStrength], areas: list[ProgramArea], exists: bool = True
) -> ProgramResponse:
    return ProgramResponse(
        student_id=uuid.uuid4(),
        exists=exists,
        strengths=strengths,
        areas_to_strengthen=areas,
    )


def _strength(name: str) -> ProgramStrength:
    return ProgramStrength(skill_id=uuid.uuid4(), skill_name=name)


def _area(name: str, rating: MeetingRating) -> ProgramArea:
    return ProgramArea(skill_id=uuid.uuid4(), skill_name=name, rating=rating)


def test_html_lists_strengths_and_areas_with_ratings() -> None:
    program = _program(
        [_strength("הגעה בזמן")],
        [_area("עבודת צוות", MeetingRating.YELLOW), _area("יוזמה", MeetingRating.RED)],
    )

    html = FociDocument(BrandSettings()).to_html(program, _issue())

    assert 'dir="rtl"' in html
    assert "מוקדי כוח ומוקדים לחיזוק" in html
    assert "הגעה בזמן" in html
    assert "עבודת צוות" in html
    assert "בהשגחה" in html
    assert "יוזמה" in html
    assert "בתלות" in html


def test_empty_sections_show_a_placeholder() -> None:
    html = FociDocument(BrandSettings()).to_html(_program([], []), _issue())

    assert "אין מוקדי כוח." in html
    assert "אין מוקדים לחיזוק." in html


def test_missing_program_shows_a_placeholder() -> None:
    html = FociDocument(BrandSettings()).to_html(_program([], [], exists=False), _issue())

    assert "עדיין לא סומנו מוקדים." in html


def test_skill_names_are_escaped() -> None:
    html = FociDocument(BrandSettings()).to_html(_program([_strength("<b>x</b>")], []), _issue())

    assert "<b>x</b>" not in html
    assert "&lt;b&gt;" in html
