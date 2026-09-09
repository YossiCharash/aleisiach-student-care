import uuid

from backend.app.client.program.program_repository import ProgramRepository
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program import Program
from backend.app.models.client.program_entry import ProgramEntry
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_entry_response import ProgramEntryResponse
from backend.app.schema.routes.program_response import ProgramResponse
from backend.app.schema.routes.program_strength import ProgramStrength
from backend.app.schema.routes.program_upsert_request import ProgramUpsertRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.resolved_focus import ResolvedFocus
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.service.taxonomy.skill_focus_resolver import SkillFocusResolver

_ENTITY_TYPE = "program"


class ProgramService:
    def __init__(
        self,
        program_repository: ProgramRepository,
        access_guard: StudentAccessGuard,
        resolver: SkillFocusResolver,
        audit_logger: AuditLogger,
    ) -> None:
        self._programs = program_repository
        self._guard = access_guard
        self._resolver = resolver
        self._audit = audit_logger

    def get_for_student(self, student_id: uuid.UUID, scope: StudentAccessScope) -> ProgramResponse:
        self._guard.require(student_id, scope)
        program = self._programs.get_for_student(student_id)
        return self._to_response(student_id, program)

    def upsert(
        self,
        student_id: uuid.UUID,
        request: ProgramUpsertRequest,
        scope: StudentAccessScope,
        author_id: uuid.UUID,
    ) -> ProgramResponse:
        self._guard.require(student_id, scope)
        resolved = self._resolver.resolve(request.entries)
        program = self._programs.get_for_student(student_id)
        action = AuditAction.CREATE if program is None else AuditAction.UPDATE
        if program is None:
            program = Program(student_id=student_id, author_id=author_id)
            program.entries = self._build_entries(resolved)
            self._programs.add(program)
        else:
            program.entries = self._build_entries(resolved)
            self._programs.flush()
        self._audit.record(
            AuditEntry(
                actor_id=author_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=program.id,
                changes=["entries"],
            )
        )
        return self._to_response(student_id, program)

    def _build_entries(self, resolved: list[ResolvedFocus]) -> list[ProgramEntry]:
        return [
            ProgramEntry(
                skill_id=item.skill_id,
                skill_name_snapshot=item.skill_name,
                rating=item.rating,
                position=position,
            )
            for position, item in enumerate(resolved)
        ]

    def _to_response(self, student_id: uuid.UUID, program: Program | None) -> ProgramResponse:
        if program is None:
            return ProgramResponse(student_id=student_id, exists=False)
        strengths: list[ProgramStrength] = []
        areas: list[ProgramArea] = []
        for entry in program.entries:
            if entry.rating == MeetingRating.GREEN:
                strengths.append(
                    ProgramStrength(skill_id=entry.skill_id, skill_name=entry.skill_name_snapshot)
                )
            else:
                areas.append(
                    ProgramArea(
                        skill_id=entry.skill_id,
                        skill_name=entry.skill_name_snapshot,
                        rating=entry.rating,
                    )
                )
        return ProgramResponse(
            student_id=student_id,
            exists=True,
            entries=[ProgramEntryResponse.model_validate(entry) for entry in program.entries],
            strengths=strengths,
            areas_to_strengthen=areas,
        )
