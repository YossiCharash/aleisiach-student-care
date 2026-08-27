from datetime import datetime

from pydantic import BaseModel


class ErrorAlert(BaseModel):
    reference: str
    error_type: str
    message: str
    method: str
    path: str
    environment: str
    occurred_at: datetime
