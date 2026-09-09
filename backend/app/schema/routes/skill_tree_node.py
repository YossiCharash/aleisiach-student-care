import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.solution_tree_node import SolutionTreeNode


class SkillTreeNode(BaseModel):
    id: uuid.UUID
    name: str
    green_text: str
    yellow_text: str
    red_text: str
    solutions: list[SolutionTreeNode] = Field(default_factory=list)
