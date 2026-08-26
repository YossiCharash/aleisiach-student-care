import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class SubLabel(OrderedTaxonomyNode):
    __tablename__ = "sub_labels"

    label_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labels.id"), nullable=False)
