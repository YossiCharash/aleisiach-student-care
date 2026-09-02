from datetime import datetime

from pydantic import BaseModel


class ErrorAlert(BaseModel):
    reference: str
    error_type: str
    method: str
    path: str
    environment: str
    institution: str | None = None
    occurred_at: datetime
