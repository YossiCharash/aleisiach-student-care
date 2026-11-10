import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain
from backend.app.models.client.risk_level import RiskLevel
from backend.app.schema.routes.risk_assessment_entry_response import RiskAssessmentEntryResponse
from backend.app.schema.routes.risk_assessment_history_response import (
    RiskAssessmentHistoryResponse,
)
from backend.app.schema.routes.risk_domain_response import RiskDomainResponse
from backend.app.schema.routes.risk_item_response import RiskItemResponse
from backend.app.schema.routes.staff_member_response import StaffMemberResponse
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.risk_assessment_document import RiskAssessmentDocument

_DOMAINS = [
    RiskDomainResponse(
        domain=RiskDomain.WEIGHT,
        category=RiskCategory.MEDICAL,
        category_label="רפואי",
        label="עודף / חוסר משקל",
    ),
    RiskDomainResponse(
        domain=RiskDomain.HARM,
        category=RiskCategory.BEHAVIORAL,
        category_label="התנהגותי",
        label="פגיעה עצמית",
    ),
]


def _issue() -> IssueContext:
    return IssueContext(
        institution_name="מוסד בדיקה",
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 9, 23),
    )


def _entry(assessment_date: date = date(2026, 9, 1)) -> RiskAssessmentEntryResponse:
    now = datetime.now(UTC)
    return RiskAssessmentEntryResponse(
        id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        assessment_date=assessment_date,
        items=[
            RiskItemResponse(
                domain=RiskDomain.WEIGHT,
                nature="אוכל <מהר>",
                level=RiskLevel.HIGH,
                intervention_plan="תפריט מסודר",
                responsible=[
                    StaffMemberResponse(id=uuid.uuid4(), full_name="דנה"),
                    StaffMemberResponse(id=uuid.uuid4(), full_name="יוסי"),
                ],
            )
        ],
        author_id=uuid.uuid4(),
        author_name="כותבת",
        created_at=now,
        updated_at=now,
    )


def _history(*entries: RiskAssessmentEntryResponse) -> RiskAssessmentHistoryResponse:
    return RiskAssessmentHistoryResponse(
        student_id=uuid.uuid4(), student_name="נועה", domains=_DOMAINS, entries=list(entries)
    )


def test_single_html_renders_table_with_categories_and_values() -> None:
    html = RiskAssessmentDocument(BrandSettings()).single_html(_history(_entry()), _issue())

    assert "ניהול סיכונים" in html
    assert "רפואי" in html and "התנהגותי" in html
    assert "עודף / חוסר משקל" in html and "פגיעה עצמית" in html
    assert "גבוה" in html
    assert "דנה, יוסי" in html
    assert "אוכל &lt;מהר&gt;" in html
    assert "כותבת" in html


def test_combined_html_shows_each_date() -> None:
    history = _history(_entry(date(2026, 6, 1)), _entry(date(2026, 1, 1)))

    html = RiskAssessmentDocument(BrandSettings()).combined_html(history, _issue())

    assert html.count('class="entry-date"') == 2


def test_empty_history_renders_placeholder() -> None:
    html = RiskAssessmentDocument(BrandSettings()).combined_html(_history(), _issue())

    assert "אין טבלאות ניהול סיכונים להצגה" in html
