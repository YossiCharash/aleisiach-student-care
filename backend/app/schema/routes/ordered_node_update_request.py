from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NodeName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class OrderedNodeUpdateRequest(BaseModel):
    name: NodeName | None = None
    order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
