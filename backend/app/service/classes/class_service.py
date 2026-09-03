import uuid
from datetime import UTC, datetime

from backend.app.client.classes.class_repository import ClassRepository
from backend.app.errors.service.class_not_empty_error import ClassNotEmptyError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.class_entity import ClassEntity
from backend.app.schema.routes.class_create_request import ClassCreateRequest
from backend.app.schema.routes.class_response import ClassResponse
from backend.app.schema.routes.class_update_request import ClassUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder

_ENTITY_TYPE = "class"


class ClassService:
    def __init__(self, classes: ClassRepository, audit_logger: AuditLogger) -> None:
        self._classes = classes
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)

    def list_active(self) -> list[ClassResponse]:
        return [ClassResponse.model_validate(entity) for entity in self._classes.list_active()]

    def list_archived(self) -> list[ClassResponse]:
        return [ClassResponse.model_validate(entity) for entity in self._classes.list_archived()]

    def create(self, request: ClassCreateRequest, actor_id: uuid.UUID) -> ClassResponse:
        entity = ClassEntity(name=request.name)
        self._classes.add(entity)
        self._audit.record(actor_id, AuditAction.CREATE, entity.id, ["name"])
        return ClassResponse.model_validate(entity)

    def rename(
        self, class_id: uuid.UUID, request: ClassUpdateRequest, actor_id: uuid.UUID
    ) -> ClassResponse:
        entity = self._require(class_id)
        entity.name = request.name
        self._audit.record(actor_id, AuditAction.UPDATE, entity.id, ["name"])
        return ClassResponse.model_validate(entity)

    def archive(self, class_id: uuid.UUID, actor_id: uuid.UUID) -> ClassResponse:
        entity = self._require(class_id)
        self._require_empty(class_id)
        entity.is_archived = True
        entity.archived_at = datetime.now(UTC)
        entity.archived_by = actor_id
        self._audit.record(actor_id, AuditAction.ARCHIVE, entity.id, ["is_archived"])
        return ClassResponse.model_validate(entity)

    def restore(self, class_id: uuid.UUID, actor_id: uuid.UUID) -> ClassResponse:
        entity = self._require(class_id)
        entity.is_archived = False
        entity.archived_at = None
        entity.archived_by = None
        self._audit.record(actor_id, AuditAction.UPDATE, entity.id, ["is_archived"])
        return ClassResponse.model_validate(entity)

    def _require_empty(self, class_id: uuid.UUID) -> None:
        students = self._classes.count_active_students(class_id)
        users = self._classes.count_enabled_users(class_id)
        if students or users:
            raise ClassNotEmptyError(students, users)

    def _require(self, class_id: uuid.UUID) -> ClassEntity:
        entity = self._classes.get(class_id)
        if entity is None:
            raise NotFoundError("class")
        return entity
