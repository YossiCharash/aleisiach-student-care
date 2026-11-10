import uuid

from backend.app.client.reports.risk_assessment_repository import RiskAssessmentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_responsible_user_error import (
    InvalidResponsibleUserError,
)
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.risk_assessment import RiskAssessment
from backend.app.models.client.risk_domain_catalog import (
    RISK_CATEGORY_LABELS,
    RISK_DOMAIN_CATALOG,
)
from backend.app.models.client.student import Student
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.risk_assessment_entry_response import RiskAssessmentEntryResponse
from backend.app.schema.routes.risk_assessment_history_response import (
    RiskAssessmentHistoryResponse,
)
from backend.app.schema.routes.risk_assessment_request import RiskAssessmentRequest
from backend.app.schema.routes.risk_domain_response import RiskDomainResponse
from backend.app.schema.routes.risk_item_fields import RiskItemFields
from backend.app.schema.routes.risk_item_response import RiskItemResponse
from backend.app.schema.routes.staff_member_response import StaffMemberResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "risk_assessment"


class RiskAssessmentService:
    def __init__(
        self,
        assessment_repository: RiskAssessmentRepository,
        user_repository: UserRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._assessments = assessment_repository
        self._users = user_repository
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

    def history(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> RiskAssessmentHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, self._assessments.list_for_student(student_id))

    def entry_history(
        self, student_id: uuid.UUID, assessment_id: uuid.UUID, scope: StudentAccessScope
    ) -> RiskAssessmentHistoryResponse:
        student = self._guard.require(student_id, scope)
        return self._build_history(student, [self._require(student_id, assessment_id)])

    def responsible_candidates(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[StaffMemberResponse]:
        student = self._guard.require(student_id, scope)
        return [
            StaffMemberResponse(id=user.id, full_name=user.full_name)
            for user in self._users.list_all()
            if user.institution_id == student.institution_id and user.status != UserStatus.DISABLED
        ]

    def create(
        self,
        student_id: uuid.UUID,
        request: RiskAssessmentRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> RiskAssessmentEntryResponse:
        student = self._guard.require(student_id, scope)
        items = self._normalized(request.items)
        self._validate_responsible(student, items)
        assessment = RiskAssessment(
            student_id=student_id,
            author_id=author_id,
            assessment_date=request.assessment_date,
            items=self._stored(items),
        )
        self._assessments.add(assessment)
        self._record(author_id, AuditAction.CREATE, assessment.id, ["assessment_date", "items"])
        return self._to_response(assessment)

    def update(
        self,
        student_id: uuid.UUID,
        assessment_id: uuid.UUID,
        request: RiskAssessmentRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> RiskAssessmentEntryResponse:
        student = self._guard.require(student_id, scope)
        assessment = self._require(student_id, assessment_id)
        items = self._normalized(request.items)
        self._validate_responsible(student, items)
        changes = self._changes(assessment, request, items)
        assessment.assessment_date = request.assessment_date
        assessment.items = self._stored(items)
        self._assessments.flush()
        self._record(actor_id, AuditAction.UPDATE, assessment.id, changes)
        return self._to_response(assessment)

    def archive(
        self,
        student_id: uuid.UUID,
        assessment_id: uuid.UUID,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> RiskAssessmentEntryResponse:
        self._guard.require(student_id, scope)
        assessment = self._require(student_id, assessment_id)
        assessment.is_archived = True
        assessment.archived_at = self._clock.now()
        assessment.archived_by = actor_id
        self._assessments.flush()
        self._record(actor_id, AuditAction.ARCHIVE, assessment.id, ["is_archived"])
        return self._to_response(assessment)

    def _normalized(self, items: list[RiskItemFields]) -> list[RiskItemFields]:
        by_domain = {item.domain: item for item in items}
        return [
            by_domain.get(domain, RiskItemFields(domain=domain))
            for domain, _, _ in RISK_DOMAIN_CATALOG
        ]

    def _stored_items(self, assessment: RiskAssessment) -> list[RiskItemFields]:
        return self._normalized([RiskItemFields.model_validate(item) for item in assessment.items])

    def _stored(self, items: list[RiskItemFields]) -> list[dict[str, object]]:
        return [item.model_dump(mode="json") for item in items]

    def _validate_responsible(self, student: Student, items: list[RiskItemFields]) -> None:
        user_ids = {user_id for item in items for user_id in item.responsible_user_ids}
        for user_id in user_ids:
            user = self._users.get(user_id)
            if user is None or user.institution_id != student.institution_id:
                raise InvalidResponsibleUserError()

    def _changes(
        self,
        assessment: RiskAssessment,
        request: RiskAssessmentRequest,
        items: list[RiskItemFields],
    ) -> list[str]:
        changes = (
            ["assessment_date"] if assessment.assessment_date != request.assessment_date else []
        )
        previous = {item.domain: item for item in self._stored_items(assessment)}
        changes.extend(
            f"items.{item.domain.value}" for item in items if previous.get(item.domain) != item
        )
        return changes

    def _record(
        self,
        actor_id: uuid.UUID,
        action: AuditAction,
        assessment_id: uuid.UUID,
        changes: list[str],
    ) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=assessment_id,
                changes=changes,
            )
        )

    def _require(self, student_id: uuid.UUID, assessment_id: uuid.UUID) -> RiskAssessment:
        assessment = self._assessments.get(assessment_id)
        if assessment is None or assessment.student_id != student_id or assessment.is_archived:
            raise NotFoundError("risk_assessment")
        return assessment

    def _build_history(
        self, student: Student, assessments: list[RiskAssessment]
    ) -> RiskAssessmentHistoryResponse:
        names: dict[uuid.UUID, str | None] = {}
        return RiskAssessmentHistoryResponse(
            student_id=student.id,
            student_name=student.full_name,
            domains=self._domains(),
            entries=[self._to_response(assessment, names) for assessment in assessments],
        )

    def _domains(self) -> list[RiskDomainResponse]:
        return [
            RiskDomainResponse(
                domain=domain,
                category=category,
                category_label=RISK_CATEGORY_LABELS[category],
                label=label,
            )
            for domain, category, label in RISK_DOMAIN_CATALOG
        ]

    def _to_response(
        self,
        assessment: RiskAssessment,
        names: dict[uuid.UUID, str | None] | None = None,
    ) -> RiskAssessmentEntryResponse:
        cache = names if names is not None else {}
        return RiskAssessmentEntryResponse(
            id=assessment.id,
            student_id=assessment.student_id,
            assessment_date=assessment.assessment_date,
            items=[self._item_response(item, cache) for item in self._stored_items(assessment)],
            author_id=assessment.author_id,
            author_name=self._user_name(assessment.author_id, cache),
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        )

    def _item_response(
        self, item: RiskItemFields, cache: dict[uuid.UUID, str | None]
    ) -> RiskItemResponse:
        responsible = [
            StaffMemberResponse(id=user_id, full_name=name)
            for user_id in item.responsible_user_ids
            if (name := self._user_name(user_id, cache)) is not None
        ]
        return RiskItemResponse(**item.model_dump(), responsible=responsible)

    def _user_name(self, user_id: uuid.UUID, cache: dict[uuid.UUID, str | None]) -> str | None:
        if user_id not in cache:
            user = self._users.get(user_id)
            cache[user_id] = user.full_name if user is not None else None
        return cache[user_id]
