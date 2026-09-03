import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.app.models.client.institution import Institution


class OptionalTenantScoped:
    @declared_attr
    def institution_id(cls) -> Mapped[uuid.UUID | None]:
        return mapped_column(ForeignKey(Institution.id), nullable=True, index=True)
