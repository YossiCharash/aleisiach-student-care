from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class DiagnosisEntry(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    note: str | None = Field(default=None, max_length=500)
