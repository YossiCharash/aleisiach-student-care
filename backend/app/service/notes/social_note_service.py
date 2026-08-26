import uuid

from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.social_note import SocialNote
from backend.app.schema.routes.social_note_response import SocialNoteResponse
from backend.app.schema.routes.social_note_upsert_request import SocialNoteUpsertRequest
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
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._notes = note_repository
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

    def get(self, student_id: uuid.UUID, scope: StudentAccessScope) -> SocialNoteResponse:
        self._guard.require(student_id, scope)
        note = self._notes.get(student_id)
        return self._to_response(student_id, note)

    def upsert(
        self,
        student_id: uuid.UUID,
        request: SocialNoteUpsertRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> SocialNoteResponse:
        self._guard.require(student_id, scope)
        note = self._notes.get(student_id)
        if note is None:
            note, created = self._notes.create(
                SocialNote(
                    student_id=student_id,
                    content=request.content,
                    updated_by=actor_id,
                    updated_at=self._clock.now(),
                )
            )
        else:
            created = False
        if not created:
            self._write(note, request.content, actor_id)
            self._notes.flush()
        action = AuditAction.CREATE if created else AuditAction.UPDATE
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=student_id,
                changes=["content"],
            )
        )
        return self._to_response(student_id, note)

    def _write(self, note: SocialNote, content: str, actor_id: uuid.UUID) -> None:
        note.content = content
        note.updated_by = actor_id
        note.updated_at = self._clock.now()

    def _to_response(self, student_id: uuid.UUID, note: SocialNote | None) -> SocialNoteResponse:
        if note is None:
            return SocialNoteResponse(student_id=student_id)
        return SocialNoteResponse(
            student_id=student_id,
            content=note.content,
            updated_by=note.updated_by,
            updated_at=note.updated_at,
        )
