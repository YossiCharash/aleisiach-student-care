from pydantic import BaseModel

from backend.app.schema.routes.field_error import FieldError


class ErrorResponse(BaseModel):
    code: str
    message: str
    reference: str | None = None
    fields: list[FieldError] | None = None
