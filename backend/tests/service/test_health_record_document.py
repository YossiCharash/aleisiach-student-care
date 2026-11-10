import uuid
from datetime import UTC, date, datetime

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.models.client.health_session_type import HealthSessionType
from backend.app.schema.routes.health_domain_response import HealthDomainResponse
from backend.app.schema.routes.health_record_history_response import (
    HealthRecordHistoryResponse,
)
from backend.app.schema.routes.health_record_response import HealthRecordResponse
from backend.app.schema.routes.staff_member_response import StaffMemberResponse
from backend.app.schema.service.issue_context import IssueContext
from backend.app.service.reports.health_record_document import HealthRecordDocument

_PHYSIO = HealthDomainResponse(id=uuid.uuid4(), name="פיזיותרפיה", order=0, is_active=True)
_SPEECH = HealthDomainResponse(id=uuid.uuid4(), name="קלינאות תקשורת", order=1, is_active=True)


def _issue() -> IssueContext:
    return IssueContext(
        institution_name="מוסד בדיקה",
        student_name="נועה",
        issued_by="מפיקה",
        issue_date=date(2026, 9, 23),
    )


def _record(domain: HealthDomainResponse) -> HealthRecordResponse:
    now = datetime.now(UTC)
    return HealthRecordResponse(
        id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        domain_id=domain.id,
        record_date=date(2026, 9, 1),
        session_type=HealthSessionType.GROUP,
        support_given="תרגול <הליכה>",
        responsible_user_ids=[],
        responsible=[StaffMemberResponse(id=uuid.uuid4(), full_name="דנה")],
        notes="",
        execution_review="בוצע",
        author_id=uuid.uuid4(),
        created_at=now,
        updated_at=now,
    )


def _history(entries: list[HealthRecordResponse]) -> HealthRecordHistoryResponse:
    return HealthRecordHistoryResponse(
        student_id=uuid.uuid4(), student_name="נועה", domains=[_PHYSIO, _SPEECH], entries=entries
    )


def test_renders_one_table_per_domain_with_rows() -> None:
    html = HealthRecordDocument(BrandSettings()).html(_history([_record(_PHYSIO)]), _issue())

    assert "תיעוד אישי – מקצועות הבריאות" in html
    assert "תחום: פיזיותרפיה" in html
    assert "קלינאות תקשורת" not in html
    assert "קבוצתי" in html
    assert "דנה" in html
    assert "בקרת ביצוע" in html
    assert "&lt;הליכה&gt;" in html


def test_renders_empty_message_without_rows() -> None:
    html = HealthRecordDocument(BrandSettings()).html(_history([]), _issue())

    assert "אין רשומות תיעוד להצגה." in html
