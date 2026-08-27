from pydantic import BaseModel


class FieldError(BaseModel):
    field: str
    message: str
