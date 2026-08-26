import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.sub_label_tree_node import SubLabelTreeNode


class LabelTreeNode(BaseModel):
    id: uuid.UUID
    name: str
    sub_labels: list[SubLabelTreeNode] = Field(default_factory=list)
