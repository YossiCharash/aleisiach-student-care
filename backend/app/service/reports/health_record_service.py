import uuid

from backend.app.client.reports.health_domain_repository import HealthDomainRepository
from backend.app.client.reports.health_record_repository import HealthRecordRepository
from backend.app.errors.service.invalid_health_domain_error import InvalidHealthDomainError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.health_domain import HealthDomain
from backend.app.models.client.health_record import HealthRecord
from backend.app.models.client.student import Student
from backend.app.schema.routes.health_domain_response import HealthDomainResponse
from backend.app.schema.routes.health_record_history_response import (
    HealthRecordHistoryResponse,
)
from backend.app.schema.routes.health_record_request import HealthRecordRequest
from backend.app.schema.routes.health_record_response import HealthRecordResponse
from backend.app.schema.routes.staff_member_response import StaffMemberResponse
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.users.responsible_user_resolver import ResponsibleUserResolver
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "health_record"

_EDITABLE_FIELDS = (
    "domain_id",
    "record_date",
    "session_type",
    "support_given",
    "responsible_user_ids",
    "notes",
    "execution_review",
)


class HealthRecordService:
    def __init__(
        self,
        record_repository: HealthRecordRepository,
        domain_repository: HealthDomainRepository,
        responsible_resolver: ResponsibleUserResolver,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._records = record_repository
        self._domains = domain_repository
        self._responsible = responsible_resolver
        self._guard = access_guard
        self._audit = EntityAuditRecorder(audit_logger, _ENTITY_TYPE)
        self._clock = clock

    def history(
        self,
        student_id: uuid.UUID,
        scope: StudentAccessScope,
        domain_id: uuid.UUID | None = None,
    ) -> HealthRecordHistoryResponse:
        student = self._guard.require(student_id, scope)
        records = self._records.list_for_student(student_id, domain_id)
        return self._build_history(student, records, domain_id)

    def responsible_candidates(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[StaffMemberResponse]:
        return self._responsible.candidates(self._guard.require(student_id, scope))

    def create(
        self,
        student_id: uuid.UUID,
        request: HealthRecordRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> HealthRecordResponse:
        student = self._guard.require(student_id, scope)
        self._require_domain(request.domain_id, None)
        names = self._responsible.validate(student, request.responsible_user_ids, set())
        record = HealthRecord(student_id=student_id, author_id=author_id)
        self._apply(record, request)
        self._records.add(record)
        self._audit.record(author_id, AuditAction.CREATE, record.id, list(_EDITABLE_FIELDS))
        return self._to_response(record, names)

    def update(
        self,
        student_id: uuid.UUID,
        record_id: uuid.UUID,
        request: HealthRecordRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> HealthRecordResponse:
        student = self._guard.require(student_id, scope)
        record = self._require(student_id, record_id)
        self._require_domain(request.domain_id, record.domain_id)
        already_assigned = {uuid.UUID(value) for value in record.responsible_user_ids}
        names = self._responsible.validate(student, request.responsible_user_ids, already_assigned)
        before = self._snapshot(record)
        self._apply(record, request)
        changes = [field for field in _EDITABLE_FIELDS if before[field] != getattr(record, field)]
        self._records.flush()
        if changes:
            self._audit.record(actor_id, AuditAction.UPDATE, record.id, changes)
        return self._to_response(record, names)

    def archive(
        self,
        student_id: uuid.UUID,
        record_id: uuid.UUID,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> HealthRecordResponse:
        self._guard.require(student_id, scope)
        record = self._require(student_id, record_id)
        record.is_archived = True
        record.archived_at = self._clock.now()
        record.archived_by = actor_id
        self._records.flush()
        self._audit.record(actor_id, AuditAction.ARCHIVE, record.id, ["is_archived"])
        return self._to_response(record, {})

    def _apply(self, record: HealthRecord, request: HealthRecordRequest) -> None:
        record.domain_id = request.domain_id
        record.record_date = request.record_date
        record.session_type = request.session_type
        record.support_given = request.support_given.strip()
        record.responsible_user_ids = [str(user_id) for user_id in request.responsible_user_ids]
        record.notes = request.notes.strip()
        record.execution_review = request.execution_review.strip()

    def _snapshot(self, record: HealthRecord) -> dict[str, object]:
        return {field: getattr(record, field) for field in _EDITABLE_FIELDS}

    def _require_domain(self, domain_id: uuid.UUID, current_domain_id: uuid.UUID | None) -> None:
        domain = self._domains.get(domain_id)
        if domain is None:
            raise InvalidHealthDomainError()
        if not domain.is_active and domain_id != current_domain_id:
            raise InvalidHealthDomainError()

    def _require(self, student_id: uuid.UUID, record_id: uuid.UUID) -> HealthRecord:
        record = self._records.get(record_id)
        if record is None or record.student_id != student_id or record.is_archived:
            raise NotFoundError("health_record")
        return record

    def _build_history(
        self,
        student: Student,
        records: list[HealthRecord],
        domain_id: uuid.UUID | None,
    ) -> HealthRecordHistoryResponse:
        names: dict[uuid.UUID, str | None] = {}
        referenced = {record.domain_id for record in records}
        return HealthRecordHistoryResponse(
            student_id=student.id,
            student_name=student.full_name,
            domains=[
                HealthDomainResponse.model_validate(domain)
                for domain in self._domains.list(include_inactive=True)
                if self._shows(domain, referenced, domain_id)
            ],
            entries=[self._to_response(record, names) for record in records],
        )

    def _shows(
        self, domain: HealthDomain, referenced: set[uuid.UUID], domain_id: uuid.UUID | None
    ) -> bool:
        if domain_id is not None:
            return domain.id == domain_id
        return domain.is_active or domain.id in referenced

    def _to_response(
        self, record: HealthRecord, cache: dict[uuid.UUID, str | None]
    ) -> HealthRecordResponse:
        user_ids = [uuid.UUID(value) for value in record.responsible_user_ids]
        return HealthRecordResponse(
            id=record.id,
            student_id=record.student_id,
            domain_id=record.domain_id,
            record_date=record.record_date,
            session_type=record.session_type,
            support_given=record.support_given,
            responsible_user_ids=user_ids,
            responsible=self._responsible.members(user_ids, cache),
            notes=record.notes,
            execution_review=record.execution_review,
            author_id=record.author_id,
            author_name=self._responsible.name(record.author_id, cache),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
