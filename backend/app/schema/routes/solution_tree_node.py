import uuid

from pydantic import BaseModel


class SolutionTreeNode(BaseModel):
    id: uuid.UUID
    text: str
