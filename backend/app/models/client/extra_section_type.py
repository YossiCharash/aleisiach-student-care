import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class ExtraSectionType(OrderedTaxonomyNode):
    __tablename__ = "extra_section_types"

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extra_section_types.id"), nullable=True
    )
