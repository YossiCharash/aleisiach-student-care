import uuid

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class SubLabel(OrderedTaxonomyNode):
    __tablename__ = "sub_labels"
    __table_args__ = (
        ForeignKeyConstraint(
            ["label_id", "institution_id"],
            ["labels.id", "labels.institution_id"],
            name="fk_sub_labels_label_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_sub_labels_id_institution"),
    )

    label_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
