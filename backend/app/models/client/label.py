from sqlalchemy import UniqueConstraint

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class Label(OrderedTaxonomyNode):
    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("id", "institution_id", name="uq_labels_id_institution"),)
