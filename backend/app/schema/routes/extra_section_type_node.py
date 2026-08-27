import uuid

from pydantic import BaseModel, Field


class ExtraSectionTypeNode(BaseModel):
    id: uuid.UUID
    name: str
    children: list["ExtraSectionTypeNode"] = Field(default_factory=list)
