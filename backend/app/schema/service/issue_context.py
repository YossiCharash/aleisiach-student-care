from datetime import date

from pydantic import BaseModel


class IssueContext(BaseModel):
    institution_name: str
    student_name: str
    issued_by: str
    issue_date: date
