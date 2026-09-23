from datetime import date

from pydantic import BaseModel

from backend.app.schema.service.issue_context import IssueContext


class DocumentMeta(BaseModel):
    title: str
    institution_name: str
    student_name: str
    issued_by: str
    issue_date: date
    content_date: date | None = None

    @classmethod
    def build(
        cls, title: str, issue: IssueContext, content_date: date | None = None
    ) -> "DocumentMeta":
        return cls(
            title=title,
            institution_name=issue.institution_name,
            student_name=issue.student_name,
            issued_by=issue.issued_by,
            issue_date=issue.issue_date,
            content_date=content_date,
        )
