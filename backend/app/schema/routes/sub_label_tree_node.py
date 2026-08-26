import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.skill_tree_node import SkillTreeNode


class SubLabelTreeNode(BaseModel):
    id: uuid.UUID
    name: str
    skills: list[SkillTreeNode] = Field(default_factory=list)
