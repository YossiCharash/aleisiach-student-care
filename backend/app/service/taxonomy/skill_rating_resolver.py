import uuid
from collections.abc import Sequence

from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_skill_rating_error import InvalidSkillRatingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.schema.service.resolved_skill_rating import ResolvedSkillRating
from backend.app.schema.service.resolved_solution import ResolvedSolution
from backend.app.schema.service.skill_rating_input import SkillRatingInput

_RATINGS_REQUIRING_SOLUTION = frozenset({MeetingRating.YELLOW, MeetingRating.RED})


class SkillRatingResolver:
    def __init__(self, taxonomy_repository: TaxonomyRepository) -> None:
        self._taxonomy = taxonomy_repository

    def resolve(self, entries: Sequence[SkillRatingInput]) -> list[ResolvedSkillRating]:
        self._reject_duplicate_skills(entries)
        return [self._resolve_entry(entry) for entry in entries]

    def _resolve_entry(self, entry: SkillRatingInput) -> ResolvedSkillRating:
        skill = self._require_skill(entry.skill_id)
        self._validate_rating(entry)
        self._reject_duplicate_solutions(entry)
        solutions = [
            self._resolve_solution(solution_id, skill) for solution_id in entry.solution_ids
        ]
        return ResolvedSkillRating(
            skill_id=skill.id,
            skill_name=skill.name,
            rating=entry.rating,
            solutions=solutions,
        )

    def _reject_duplicate_skills(self, entries: Sequence[SkillRatingInput]) -> None:
        skill_ids = [entry.skill_id for entry in entries]
        if len(set(skill_ids)) != len(skill_ids):
            raise InvalidSkillRatingError("a skill appears more than once")

    def _validate_rating(self, entry: SkillRatingInput) -> None:
        needs_solution = entry.rating in _RATINGS_REQUIRING_SOLUTION
        if needs_solution and not entry.solution_ids:
            raise InvalidSkillRatingError("a solution is required for a yellow or red rating")
        if not needs_solution and entry.solution_ids:
            raise InvalidSkillRatingError("a green rating cannot have solutions")

    def _reject_duplicate_solutions(self, entry: SkillRatingInput) -> None:
        if len(set(entry.solution_ids)) != len(entry.solution_ids):
            raise InvalidSkillRatingError("a solution was chosen more than once")

    def _resolve_solution(self, solution_id: uuid.UUID, skill: Skill) -> ResolvedSolution:
        solution = self._require_solution(solution_id)
        if solution.skill_id != skill.id:
            raise InvalidSkillRatingError("a solution does not belong to its skill")
        return ResolvedSolution(solution_id=solution.id, solution_text=solution.text)

    def _require_skill(self, skill_id: uuid.UUID) -> Skill:
        skill = self._taxonomy.get_skill(skill_id)
        if skill is None:
            raise NotFoundError("skill")
        return skill

    def _require_solution(self, solution_id: uuid.UUID) -> Solution:
        solution = self._taxonomy.get_solution(solution_id)
        if solution is None:
            raise NotFoundError("solution")
        return solution
