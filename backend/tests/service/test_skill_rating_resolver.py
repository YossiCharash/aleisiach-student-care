import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_skill_rating_error import InvalidSkillRatingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.solution import Solution
from backend.app.models.client.sub_label import SubLabel
from backend.app.schema.routes.skill_rating_request import SkillRatingRequest
from backend.app.service.taxonomy.skill_rating_resolver import SkillRatingResolver


class _Fixture:
    def __init__(
        self,
        resolver: SkillRatingResolver,
        skill: uuid.UUID,
        other_skill: uuid.UUID,
        solution: uuid.UUID,
        other_solution: uuid.UUID,
    ) -> None:
        self.resolver = resolver
        self.skill = skill
        self.other_skill = other_skill
        self.solution = solution
        self.other_solution = other_solution


def _setup(session: Session) -> _Fixture:
    label = Label(name="עצמאות")
    session.add(label)
    session.flush()
    sub_label = SubLabel(label_id=label.id, name="היגיינה")
    session.add(sub_label)
    session.flush()
    skill = Skill(sub_label_id=sub_label.id, name="רחיצת ידיים")
    other_skill = Skill(sub_label_id=sub_label.id, name="צחצוח שיניים")
    session.add_all([skill, other_skill])
    session.flush()
    solution = Solution(skill_id=skill.id, text="תרגול יומי")
    other_solution = Solution(skill_id=other_skill.id, text="פתרון אחר")
    session.add_all([solution, other_solution])
    session.flush()
    return _Fixture(
        SkillRatingResolver(TaxonomyRepository(session)),
        skill.id,
        other_skill.id,
        solution.id,
        other_solution.id,
    )


def test_resolves_snapshots(db_session: Session) -> None:
    fx = _setup(db_session)

    resolved = fx.resolver.resolve(
        [
            SkillRatingRequest(
                skill_id=fx.skill, rating=MeetingRating.YELLOW, solution_ids=[fx.solution]
            )
        ]
    )

    assert resolved[0].skill_name == "רחיצת ידיים"
    assert resolved[0].solutions[0].solution_text == "תרגול יומי"


def test_duplicate_skill_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)

    with pytest.raises(InvalidSkillRatingError):
        fx.resolver.resolve(
            [
                SkillRatingRequest(skill_id=fx.skill, rating=MeetingRating.GREEN),
                SkillRatingRequest(skill_id=fx.skill, rating=MeetingRating.GREEN),
            ]
        )


def test_green_with_solution_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)

    with pytest.raises(InvalidSkillRatingError):
        fx.resolver.resolve(
            [
                SkillRatingRequest(
                    skill_id=fx.skill, rating=MeetingRating.GREEN, solution_ids=[fx.solution]
                )
            ]
        )


def test_solution_from_another_skill_is_rejected(db_session: Session) -> None:
    fx = _setup(db_session)

    with pytest.raises(InvalidSkillRatingError):
        fx.resolver.resolve(
            [
                SkillRatingRequest(
                    skill_id=fx.skill,
                    rating=MeetingRating.YELLOW,
                    solution_ids=[fx.other_solution],
                )
            ]
        )


def test_unknown_skill_is_not_found(db_session: Session) -> None:
    fx = _setup(db_session)

    with pytest.raises(NotFoundError):
        fx.resolver.resolve([SkillRatingRequest(skill_id=uuid.uuid4(), rating=MeetingRating.GREEN)])
