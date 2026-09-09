import uuid

from sqlalchemy import ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class Skill(OrderedTaxonomyNode):
    __tablename__ = "skills"
    __table_args__ = (
        ForeignKeyConstraint(
            ["label_id", "institution_id"],
            ["labels.id", "labels.institution_id"],
            name="fk_skills_label_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_skills_id_institution"),
    )

    label_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    green_text: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    yellow_text: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    red_text: Mapped[str] = mapped_column(String(500), nullable=False, default="")
