import uuid

from backend.app.client.students.extra_section_type_repository import (
    ExtraSectionTypeRepository,
)
from backend.app.client.students.student_extra_section_repository import (
    StudentExtraSectionRepository,
)
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.student_extra_section import StudentExtraSection
from backend.app.schema.routes.student_extra_section_entry import StudentExtraSectionEntry
from backend.app.schema.routes.student_extra_section_upsert_request import (
    StudentExtraSectionUpsertRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard

_ENTITY_TYPE = "student_extra_section"


class StudentExtraSectionService:
    def __init__(
        self,
        section_repository: StudentExtraSectionRepository,
        type_repository: ExtraSectionTypeRepository,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
    ) -> None:
        self._sections = section_repository
        self._types = type_repository
        self._guard = access_guard
        self._audit = audit_logger

    def get_for_student(
        self, student_id: uuid.UUID, scope: StudentAccessScope
    ) -> list[StudentExtraSectionEntry]:
        self._guard.require(student_id, scope)
        content = {
            entry.section_type_id: entry.content
            for entry in self._sections.list_for_student(student_id)
        }
        return [
            StudentExtraSectionEntry(
                section_type_id=section_type.id,
                name=section_type.name,
                parent_id=section_type.parent_id,
                content=content.get(section_type.id),
            )
            for section_type in self._types.list(include_inactive=False)
        ]

    def set(
        self,
        student_id: uuid.UUID,
        section_type_id: uuid.UUID,
        request: StudentExtraSectionUpsertRequest,
        scope: StudentAccessScope,
        actor_id: uuid.UUID,
    ) -> StudentExtraSectionEntry:
        self._guard.require(student_id, scope)
        section_type = self._types.get(section_type_id)
        if section_type is None:
            raise NotFoundError("section_type")
        entry = self._sections.get(student_id, section_type_id)
        if entry is None:
            entry, created = self._sections.create(
                StudentExtraSection(
                    student_id=student_id,
                    section_type_id=section_type_id,
                    content=request.content,
                )
            )
            if not created:
                entry.content = request.content
                self._sections.flush()
        else:
            entry.content = request.content
            self._sections.flush()
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=entry.id,
                changes=["content"],
            )
        )
        return StudentExtraSectionEntry(
            section_type_id=section_type.id,
            name=section_type.name,
            parent_id=section_type.parent_id,
            content=entry.content,
        )
