import uuid

from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.social_note_entry import SocialNoteEntry
from backend.app.schema.routes.social_note_create_request import SocialNoteCreateRequest
from backend.app.schema.routes.social_note_entry_response import SocialNoteEntryResponse
from backend.app.schema.routes.social_note_report_response import SocialNoteReportResponse
from backend.app.schema.routes.social_note_update_request import SocialNoteUpdateRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "social_note"


class SocialNoteService:
    def __init__(
        self,
        note_repository: SocialNoteRepository,
        user_repository: UserRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._notes = note_repository
        self._users = user_repository
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

    def report(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> SocialNoteReportResponse:
        student = self._guard.require(student_id, scope)
        entries = self._notes.list_for_student(student_id)
        return SocialNoteReportResponse(
            student_id=student_id,
            student_name=student.full_name,
            entries=[self._to_response(entry) for entry in entries],
        )

    def entry_report(
        self, student_id: uuid.UUID, entry_id: uuid.UUID, scope: StudentAccessScope
    ) -> SocialNoteReportResponse:
        student = self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        return SocialNoteReportResponse(
            student_id=student_id,
            student_name=student.full_name,
            entries=[self._to_response(entry)],
        )

    def create(
        self,
        student_id: uuid.UUID,
        request: SocialNoteCreateRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> SocialNoteEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._notes.add(
            SocialNoteEntry(
                student_id=student_id,
                note_date=request.note_date,
                content=request.content,
                author_id=author_id,
            )
        )
        self._audit.record(
            AuditEntry(
                actor_id=author_id,
                action=AuditAction.CREATE,
                entity_type=_ENTITY_TYPE,
                entity_id=entry.id,
                changes=["note_date", "content"],
            )
        )
        return self._to_response(entry)

    def update(
        self,
        student_id: uuid.UUID,
        entry_id: uuid.UUID,
        request: SocialNoteUpdateRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> SocialNoteEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        entry.content = request.content
        self._notes.flush()
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=entry.id,
                changes=["content"],
            )
        )
        return self._to_response(entry)

    def archive(
        self,
        student_id: uuid.UUID,
        entry_id: uuid.UUID,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> SocialNoteEntryResponse:
        self._guard.require(student_id, scope)
        entry = self._require_entry(student_id, entry_id)
        entry.is_archived = True
        entry.archived_at = self._clock.now()
        entry.archived_by = actor_id
        self._notes.flush()
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.ARCHIVE,
                entity_type=_ENTITY_TYPE,
                entity_id=entry.id,
                changes=["is_archived"],
            )
        )
        return self._to_response(entry)

    def _require_entry(self, student_id: uuid.UUID, entry_id: uuid.UUID) -> SocialNoteEntry:
        entry = self._notes.get(entry_id)
        if entry is None or entry.student_id != student_id or entry.is_archived:
            raise NotFoundError("social_note")
        return entry

    def _to_response(self, entry: SocialNoteEntry) -> SocialNoteEntryResponse:
        author = self._users.get(entry.author_id)
        return SocialNoteEntryResponse(
            id=entry.id,
            student_id=entry.student_id,
            note_date=entry.note_date,
            content=entry.content,
            author_id=entry.author_id,
            author_name=author.full_name if author is not None else None,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
