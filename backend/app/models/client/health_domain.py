from sqlalchemy import UniqueConstraint

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class HealthDomain(OrderedTaxonomyNode):
    __tablename__ = "health_domains"
    __table_args__ = (
        UniqueConstraint("id", "institution_id", name="uq_health_domains_id_institution"),
    )
