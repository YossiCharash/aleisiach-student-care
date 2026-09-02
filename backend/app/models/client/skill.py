import uuid

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class Skill(OrderedTaxonomyNode):
    __tablename__ = "skills"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sub_label_id", "institution_id"],
            ["sub_labels.id", "sub_labels.institution_id"],
            name="fk_skills_sub_label_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_skills_id_institution"),
    )

    sub_label_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
