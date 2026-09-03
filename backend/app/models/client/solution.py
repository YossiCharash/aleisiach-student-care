import uuid

from sqlalchemy import Boolean, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class Solution(TenantScoped, Base):
    __tablename__ = "solutions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_solutions_skill_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_solutions_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    skill_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
