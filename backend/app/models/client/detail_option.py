import uuid

from sqlalchemy import Boolean, Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.detail_option_field import DetailOptionField


class DetailOption(Base):
    __tablename__ = "detail_options"
    __table_args__ = (UniqueConstraint("field", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    field: Mapped[DetailOptionField] = mapped_column(
        Enum(DetailOptionField, native_enum=False, length=40), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column("order", Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
