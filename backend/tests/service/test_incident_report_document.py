import uuid
from datetime import UTC, date, datetime, time

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.incident_nature import IncidentNature
from backend.app.models.client.incident_referral import IncidentReferral
from backend.app.models.client.incident_report_type import IncidentReportType
from backend.app.schema.routes.incident_report_entry_response import IncidentReportEntryResponse
from backend.app.schema.routes.incident_report_history_response import (
    IncidentReportHistoryResponse,
)
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.incident_report_document import IncidentReportDocument


def _issue() -> IssueContext:
    return IssueContext(
        institution_name="מוסד בדיקה",
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 9, 23),
    )


def _entry(**overrides: object) -> IncidentReportEntryResponse:
    now = datetime.now(UTC)
    base: dict[str, object] = {
        "id": uuid.uuid4(),
        "student_id": uuid.uuid4(),
        "event_date": date(2026, 9, 1),
        "event_time": time(9, 5),
        "location": "חצר",
        "report_type": IncidentReportType.EXTERNAL,
        "natures": [IncidentNature.OTHER],
        "nature_other": "נפילה מכיסא",
        "description": "תיאור <מפורט>",
        "referrals": [IncidentReferral.POLICE],
        "manager_updated_date": date(2026, 9, 2),
        "manager_updated_time": time(16, 0),
        "lessons_learned": "לקח חשוב",
        "filler_role": "מדריכת סדנה",
        "author_id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return IncidentReportEntryResponse.model_validate(base)


def _history(*entries: IncidentReportEntryResponse) -> IncidentReportHistoryResponse:
    return IncidentReportHistoryResponse(
        student_id=uuid.uuid4(),
        student_name="נועה",
        national_id="123456782",
        entries=list(entries),
    )


def _document() -> IncidentReportDocument:
    return IncidentReportDocument(BrandSettings())


def test_single_report_shows_recipient_identity_and_fields() -> None:
    html = _document().single_html(_history(_entry()), _issue())

    assert "דו״ח אירוע חריג" in html
    assert "נועה, ת.ז 123456782" in html
    assert "09:05" in html
    assert "חצר" in html
    assert "בשעה 16:00" in html
    assert "לקח חשוב" in html
    assert "מדריכת סדנה" in html


def test_checked_options_are_marked_and_other_text_is_shown() -> None:
    html = _document().single_html(_history(_entry()), _issue())

    assert '<span class="box checked"></span>אחר: נפילה מכיסא' in html
    assert '<span class="box checked"></span>משטרה' in html
    assert '<span class="box"></span>אלימות' in html
    assert '<span class="box checked"></span>אירוע חריג – דיווח חיצוני' in html


def test_text_is_escaped() -> None:
    html = _document().single_html(_history(_entry()), _issue())

    assert "תיאור &lt;מפורט&gt;" in html


def test_signature_line_and_attachment_note_are_printed() -> None:
    html = _document().single_html(_history(_entry()), _issue())

    assert 'class="signature-line"' in html
    assert "שם ממלא הטופס" not in html
    assert "יש לצרף לטופס" in html


def test_combined_report_heads_each_entry_with_its_date() -> None:
    html = _document().combined_html(
        _history(_entry(event_date=date(2026, 9, 1)), _entry(event_date=date(2026, 3, 4))),
        _issue(),
    )

    assert "01/09/2026" in html
    assert "04/03/2026" in html
    assert html.count('class="entry-date"') == 2


def test_empty_history_shows_placeholder() -> None:
    html = _document().combined_html(_history(), _issue())

    assert "אין דו״חות אירוע חריג להצגה." in html


def test_recipient_without_national_id_shows_name_only() -> None:
    history = _history(_entry())
    history.national_id = None

    html = _document().single_html(history, _issue())

    assert "נועה, ת.ז" not in html
