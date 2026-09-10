import uuid
from datetime import UTC, datetime

from backend.app.client.workshops.workshop_repository import WorkshopRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.errors.service.workshop_not_empty_error import WorkshopNotEmptyError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.user import User
from backend.app.models.client.workshop import Workshop
from backend.app.schema.routes.workshop_create_request import WorkshopCreateRequest
from backend.app.schema.routes.workshop_response import WorkshopResponse
from backend.app.schema.routes.workshop_update_request import WorkshopUpdateRequest
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder

_ENTITY_TYPE = "workshop"
_PERMISSION_ENTITY_TYPE = "permission"


class WorkshopService:
    def __init__(self, workshops: WorkshopRepository, audit_logger: AuditLogger) -> None:
        self._workshops = workshops
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)
        self._permissions_audit = EntityAuditRecorder(audit_logger, _PERMISSION_ENTITY_TYPE)

    def list_active(self, scope: StudentAccessScope) -> list[WorkshopResponse]:
        visible = [
            workshop for workshop in self._workshops.list_active() if scope.permits(workshop.id)
        ]
        return self._to_responses(visible)

    def list_archived(self) -> list[WorkshopResponse]:
        return self._to_responses(self._workshops.list_archived())

    def create(self, request: WorkshopCreateRequest, actor_id: uuid.UUID) -> WorkshopResponse:
        self._require_instructor_valid(request.instructor_id)
        entity = Workshop(name=request.name, color=request.color)
        self._workshops.add(entity)
        self._audit.record(actor_id, AuditAction.CREATE, entity.id, ["name", "color"])
        self._assign_instructor(entity.id, request.instructor_id, actor_id)
        return self._to_response(entity)

    def update(
        self, workshop_id: uuid.UUID, request: WorkshopUpdateRequest, actor_id: uuid.UUID
    ) -> WorkshopResponse:
        entity = self._require(workshop_id)
        self._require_instructor_valid(request.instructor_id)
        entity.name = request.name
        entity.color = request.color
        self._audit.record(actor_id, AuditAction.UPDATE, entity.id, ["name", "color"])
        self._assign_instructor(entity.id, request.instructor_id, actor_id)
        return self._to_response(entity)

    def archive(self, workshop_id: uuid.UUID, actor_id: uuid.UUID) -> WorkshopResponse:
        entity = self._require(workshop_id)
        self._require_empty(workshop_id)
        entity.is_archived = True
        entity.archived_at = datetime.now(UTC)
        entity.archived_by = actor_id
        self._audit.record(actor_id, AuditAction.ARCHIVE, entity.id, ["is_archived"])
        return self._to_response(entity)

    def restore(self, workshop_id: uuid.UUID, actor_id: uuid.UUID) -> WorkshopResponse:
        entity = self._require(workshop_id)
        entity.is_archived = False
        entity.archived_at = None
        entity.archived_by = None
        self._audit.record(actor_id, AuditAction.UPDATE, entity.id, ["is_archived"])
        return self._to_response(entity)

    def _assign_instructor(
        self, workshop_id: uuid.UUID, instructor_id: uuid.UUID | None, actor_id: uuid.UUID
    ) -> None:
        for user_id in self._workshops.assign_instructor(workshop_id, instructor_id):
            self._permissions_audit.record(actor_id, AuditAction.UPDATE, user_id, ["workshop_id"])

    def _require_instructor_valid(self, instructor_id: uuid.UUID | None) -> None:
        if instructor_id is not None and self._workshops.get_instructor(instructor_id) is None:
            raise NotFoundError("instructor")

    def _to_responses(self, entities: list[Workshop]) -> list[WorkshopResponse]:
        assigned = self._workshops.instructors_by_workshop()
        return [self._build(entity, assigned.get(entity.id)) for entity in entities]

    def _to_response(self, entity: Workshop) -> WorkshopResponse:
        return self._build(entity, self._workshops.instructor_for(entity.id))

    def _build(self, entity: Workshop, instructor: User | None) -> WorkshopResponse:
        return WorkshopResponse(
            id=entity.id,
            name=entity.name,
            color=entity.color,
            instructor_id=instructor.id if instructor is not None else None,
            instructor_name=instructor.full_name if instructor is not None else None,
        )

    def _require_empty(self, workshop_id: uuid.UUID) -> None:
        students = self._workshops.count_active_students(workshop_id)
        users = self._workshops.count_enabled_users(workshop_id)
        if students or users:
            raise WorkshopNotEmptyError(students, users)

    def _require(self, workshop_id: uuid.UUID) -> Workshop:
        entity = self._workshops.get(workshop_id)
        if entity is None:
            raise NotFoundError("workshop")
        return entity
