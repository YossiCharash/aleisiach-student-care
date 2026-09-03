import uuid

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class ExtraSectionType(OrderedTaxonomyNode):
    __tablename__ = "extra_section_types"
    __table_args__ = (
        ForeignKeyConstraint(
            ["parent_id", "institution_id"],
            ["extra_section_types.id", "extra_section_types.institution_id"],
            name="fk_extra_section_types_parent_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_extra_section_types_id_institution"),
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
