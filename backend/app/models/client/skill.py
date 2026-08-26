import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class Skill(OrderedTaxonomyNode):
    __tablename__ = "skills"

    sub_label_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sub_labels.id"), nullable=False)
