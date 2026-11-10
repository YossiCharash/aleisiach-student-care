from sqlalchemy import Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode
from backend.app.models.client.risk_category import RiskCategory


class RiskDomain(OrderedTaxonomyNode):
    __tablename__ = "risk_domains"
    __table_args__ = (
        UniqueConstraint("id", "institution_id", name="uq_risk_domains_id_institution"),
    )

    category: Mapped[RiskCategory] = mapped_column(
        Enum(RiskCategory, native_enum=False, length=16), nullable=False
    )
