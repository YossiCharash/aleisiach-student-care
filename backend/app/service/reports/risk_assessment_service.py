import uuid

from backend.app.client.reports.risk_assessment_repository import RiskAssessmentRepository
from backend.app.client.reports.risk_domain_repository import RiskDomainRepository
from backend.app.errors.service.invalid_risk_domain_error import InvalidRiskDomainError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.risk_assessment import RiskAssessment
from backend.app.models.client.risk_domain import RiskDomain
from backend.app.models.client.student import Student
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
from backend.app.service.users.responsible_user_resolver import ResponsibleUserResolver
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "risk_assessment"


class RiskAssessmentService:
    def __init__(
        self,
        assessment_repository: RiskAssessmentRepository,
        domain_repository: RiskDomainRepository,
        responsible_resolver: ResponsibleUserResolver,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._assessments = assessment_repository
        self._domains = domain_repository
        self._responsible = responsible_resolver
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
        return self._responsible.candidates(self._guard.require(student_id, scope))

    def create(
        self,
        student_id: uuid.UUID,
        request: RiskAssessmentRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> RiskAssessmentEntryResponse:
        student = self._guard.require(student_id, scope)
        catalog = self._domains.list(include_inactive=True)
        items = self._normalized(request.items, catalog, set())
        names = self._validate_responsible(student, items, set())
        assessment = RiskAssessment(
            student_id=student_id,
            author_id=author_id,
            assessment_date=request.assessment_date,
            items=self._stored(items),
        )
        self._assessments.add(assessment)
        self._record(author_id, AuditAction.CREATE, assessment.id, ["assessment_date", "items"])
        return self._to_response(assessment, catalog, names)

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
        catalog = self._domains.list(include_inactive=True)
        previous = self._stored_items(assessment, catalog)
        items = self._normalized(request.items, catalog, {item.domain_id for item in previous})
        already_assigned = {user_id for item in previous for user_id in item.responsible_user_ids}
        names = self._validate_responsible(student, items, already_assigned)
        changes = self._changes(assessment, request, previous, items)
        assessment.assessment_date = request.assessment_date
        assessment.items = self._stored(items)
        self._assessments.flush()
        self._record(actor_id, AuditAction.UPDATE, assessment.id, changes)
        return self._to_response(assessment, catalog, names)

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
        return self._to_response(assessment, self._domains.list(include_inactive=True))

    def _normalized(
        self,
        items: list[RiskItemFields],
        catalog: list[RiskDomain],
        already_present: set[uuid.UUID],
    ) -> list[RiskItemFields]:
        allowed = {
            domain.id for domain in catalog if domain.is_active or domain.id in already_present
        }
        by_domain = {item.domain_id: item for item in items}
        if not by_domain.keys() <= allowed:
            raise InvalidRiskDomainError()
        return [
            by_domain[domain.id]
            for domain in catalog
            if domain.id in by_domain and self._has_content(by_domain[domain.id])
        ]

    def _has_content(self, item: RiskItemFields) -> bool:
        return bool(
            item.nature.strip()
            or item.level is not None
            or item.intervention_plan.strip()
            or item.responsible_user_ids
        )

    def _stored_items(
        self, assessment: RiskAssessment, catalog: list[RiskDomain]
    ) -> list[RiskItemFields]:
        position = {domain.id: index for index, domain in enumerate(catalog)}
        items = [RiskItemFields.model_validate(item) for item in assessment.items]
        return sorted(
            (item for item in items if item.domain_id in position),
            key=lambda item: position[item.domain_id],
        )

    def _stored(self, items: list[RiskItemFields]) -> list[dict[str, object]]:
        return [item.model_dump(mode="json") for item in items]

    def _validate_responsible(
        self,
        student: Student,
        items: list[RiskItemFields],
        already_assigned: set[uuid.UUID],
    ) -> dict[uuid.UUID, str | None]:
        user_ids = {user_id for item in items for user_id in item.responsible_user_ids}
        return self._responsible.validate(student, user_ids, already_assigned)

    def _changes(
        self,
        assessment: RiskAssessment,
        request: RiskAssessmentRequest,
        previous: list[RiskItemFields],
        items: list[RiskItemFields],
    ) -> list[str]:
        changes = (
            ["assessment_date"] if assessment.assessment_date != request.assessment_date else []
        )
        before = {item.domain_id: item for item in previous}
        after = {item.domain_id: item for item in items}
        changes.extend(
            f"items.{domain_id}"
            for domain_id in dict.fromkeys([*before, *after])
            if before.get(domain_id) != after.get(domain_id)
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
        catalog = self._domains.list(include_inactive=True)
        entries = [self._to_response(assessment, catalog, names) for assessment in assessments]
        referenced = {item.domain_id for entry in entries for item in entry.items}
        return RiskAssessmentHistoryResponse(
            student_id=student.id,
            student_name=student.full_name,
            domains=[
                RiskDomainResponse.model_validate(domain)
                for domain in catalog
                if domain.is_active or domain.id in referenced
            ],
            entries=entries,
        )

    def _to_response(
        self,
        assessment: RiskAssessment,
        catalog: list[RiskDomain],
        names: dict[uuid.UUID, str | None] | None = None,
    ) -> RiskAssessmentEntryResponse:
        cache = names if names is not None else {}
        return RiskAssessmentEntryResponse(
            id=assessment.id,
            student_id=assessment.student_id,
            assessment_date=assessment.assessment_date,
            items=[
                self._item_response(item, cache) for item in self._stored_items(assessment, catalog)
            ],
            author_id=assessment.author_id,
            author_name=self._responsible.name(assessment.author_id, cache),
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        )

    def _item_response(
        self, item: RiskItemFields, cache: dict[uuid.UUID, str | None]
    ) -> RiskItemResponse:
        responsible = self._responsible.members(item.responsible_user_ids, cache)
        return RiskItemResponse(**item.model_dump(), responsible=responsible)
