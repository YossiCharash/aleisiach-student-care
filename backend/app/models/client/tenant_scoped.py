import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.app.models.client.institution import Institution


class TenantScoped:
    @declared_attr
    def institution_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(ForeignKey(Institution.id), nullable=False, index=True)
