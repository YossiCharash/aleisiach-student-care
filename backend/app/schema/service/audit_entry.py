import uuid

from pydantic import BaseModel, Field

from backend.app.models.client.audit_action import AuditAction


class AuditEntry(BaseModel):
    actor_id: uuid.UUID
    action: AuditAction
    entity_type: str
    entity_id: uuid.UUID
    changes: list[str] = Field(default_factory=list)
    ip: str | None = None
    user_agent: str | None = None
