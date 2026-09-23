from datetime import date

from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.schema.service.issue_context import IssueContext


def _issue() -> IssueContext:
    return IssueContext(
        institution_name="מוסד",
        student_name="נועה",
        issued_by="רונית",
        issue_date=date(2026, 9, 23),
    )


def test_build_copies_the_issue_context_fields() -> None:
    meta = DocumentMeta.build("דוח תפקודי", _issue())

    assert meta.title == "דוח תפקודי"
    assert meta.institution_name == "מוסד"
    assert meta.student_name == "נועה"
    assert meta.issued_by == "רונית"
    assert meta.issue_date == date(2026, 9, 23)
    assert meta.content_date is None


def test_build_carries_an_optional_content_date() -> None:
    meta = DocumentMeta.build("סיכום ישיבת צוות", _issue(), date(2026, 8, 15))

    assert meta.content_date == date(2026, 8, 15)
