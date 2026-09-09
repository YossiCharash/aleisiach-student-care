import uuid
from collections.abc import Sequence

from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_skill_rating_error import InvalidSkillRatingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.skill import Skill
from backend.app.schema.routes.focus_rating_request import FocusRatingRequest
from backend.app.schema.service.resolved_focus import ResolvedFocus


class SkillFocusResolver:
    def __init__(self, taxonomy_repository: TaxonomyRepository) -> None:
        self._taxonomy = taxonomy_repository

    def resolve(self, entries: Sequence[FocusRatingRequest]) -> list[ResolvedFocus]:
        self._reject_duplicate_skills(entries)
        return [self._resolve_entry(entry) for entry in entries]

    def _resolve_entry(self, entry: FocusRatingRequest) -> ResolvedFocus:
        skill = self._require_skill(entry.skill_id)
        return ResolvedFocus(skill_id=skill.id, skill_name=skill.name, rating=entry.rating)

    def _reject_duplicate_skills(self, entries: Sequence[FocusRatingRequest]) -> None:
        skill_ids = [entry.skill_id for entry in entries]
        if len(set(skill_ids)) != len(skill_ids):
            raise InvalidSkillRatingError("a skill appears more than once")

    def _require_skill(self, skill_id: uuid.UUID) -> Skill:
        skill = self._taxonomy.get_skill(skill_id)
        if skill is None:
            raise NotFoundError("skill")
        return skill
