from sqlalchemy import Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.client.detail_option_field import DetailOptionField
from backend.app.models.client.ordered_taxonomy_node import OrderedTaxonomyNode


class DetailOption(OrderedTaxonomyNode):
    __tablename__ = "detail_options"
    __table_args__ = (
        UniqueConstraint(
            "institution_id", "field", "name", name="uq_detail_options_institution_field_name"
        ),
    )

    field: Mapped[DetailOptionField] = mapped_column(
        Enum(
            DetailOptionField,
            native_enum=False,
            length=40,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
