import uuid

from backend.app.client.students.detail_option_repository import DetailOptionRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.detail_option_field import DetailOptionField
from backend.app.schema.routes.detail_option_create_request import (
    DetailOptionCreateRequest,
)
from backend.app.schema.routes.detail_option_response import DetailOptionResponse
from backend.app.schema.routes.detail_option_update_request import (
    DetailOptionUpdateRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger

_ENTITY_TYPE = "detail_option"


class DetailOptionService:
    def __init__(self, repository: DetailOptionRepository, audit_logger: AuditLogger) -> None:
        self._options = repository
        self._audit = audit_logger

    def list_all(self, include_inactive: bool) -> list[DetailOptionResponse]:
        return [
            DetailOptionResponse.model_validate(option)
            for option in self._options.list(include_inactive)
        ]

    def create(
        self, request: DetailOptionCreateRequest, actor_id: uuid.UUID
    ) -> DetailOptionResponse:
        name = request.name.strip()
        existing = self._options.get_by_field_and_name(request.field, name)
        if existing is not None:
            return DetailOptionResponse.model_validate(existing)
        option = DetailOption(
            field=request.field,
            name=name,
            order=self._options.next_order(request.field),
        )
        self._options.add(option)
        self._record(actor_id, AuditAction.CREATE, option.id, ["field", "name"])
        return DetailOptionResponse.model_validate(option)

    def update(
        self,
        option_id: uuid.UUID,
        request: DetailOptionUpdateRequest,
        actor_id: uuid.UUID,
    ) -> DetailOptionResponse:
        option = self._options.get(option_id)
        if option is None:
            raise NotFoundError("detail_option")
        changes: list[str] = []
        if request.name is not None:
            option.name = request.name.strip()
            changes.append("name")
        if request.order is not None:
            option.order = request.order
            changes.append("order")
        if request.is_active is not None:
            option.is_active = request.is_active
            changes.append("is_active")
        self._options.flush()
        self._record(actor_id, AuditAction.UPDATE, option.id, changes)
        return DetailOptionResponse.model_validate(option)

    def _record(
        self, actor_id: uuid.UUID, action: AuditAction, entity_id: uuid.UUID, changes: list[str]
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=entity_id,
                changes=changes,
            )
        )


DEFAULT_DETAIL_OPTIONS: dict[DetailOptionField, tuple[str, ...]] = {
    DetailOptionField.IDD_SEVERITY: ("קלה", "בינונית", "מורכבת"),
    DetailOptionField.MEDICATION_INDEPENDENCE: (
        "אינו נוטל לבד",
        "זקוק לתזכורת והשגחה",
        "עצמאי",
    ),
    DetailOptionField.EXPRESSION_MODE: (
        "דיבור מילולי שוטף",
        "מילים בודדות ומשפטים קצרים",
        "ג'סטות ותנועות גוף",
        "שימוש בטאבלט או אייפד",
        "לא ורבלי",
    ),
    DetailOptionField.LANGUAGE_COMPREHENSION: (
        "מבין הוראות מורכבות",
        "מבין רק הוראות פשוטות",
    ),
    DetailOptionField.ASSISTIVE_DEVICE: (
        "משקפיים",
        "מכשיר שמיעה",
        "מדרסים",
        "קביים",
        "הליכון",
        "אחר",
    ),
}
