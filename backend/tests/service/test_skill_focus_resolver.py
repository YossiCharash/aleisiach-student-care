import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.invalid_skill_rating_error import InvalidSkillRatingError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.label import Label
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.schema.routes.focus_rating_request import FocusRatingRequest
from backend.app.service.taxonomy.skill_focus_resolver import SkillFocusResolver


def _skill(session: Session) -> uuid.UUID:
    label = Label(name="L")
    session.add(label)
    session.flush()
    skill = Skill(label_id=label.id, name="רחיצה")
    session.add(skill)
    session.flush()
    return skill.id


def test_resolves_skill_name_and_rating(db_session: Session) -> None:
    skill_id = _skill(db_session)
    resolver = SkillFocusResolver(TaxonomyRepository(db_session))

    resolved = resolver.resolve([FocusRatingRequest(skill_id=skill_id, rating=MeetingRating.RED)])

    assert resolved[0].skill_name == "רחיצה"
    assert resolved[0].rating == MeetingRating.RED


def test_unknown_skill_raises(db_session: Session) -> None:
    resolver = SkillFocusResolver(TaxonomyRepository(db_session))

    with pytest.raises(NotFoundError):
        resolver.resolve([FocusRatingRequest(skill_id=uuid.uuid4(), rating=MeetingRating.GREEN)])


def test_duplicate_skill_raises(db_session: Session) -> None:
    skill_id = _skill(db_session)
    resolver = SkillFocusResolver(TaxonomyRepository(db_session))

    with pytest.raises(InvalidSkillRatingError):
        resolver.resolve(
            [
                FocusRatingRequest(skill_id=skill_id, rating=MeetingRating.GREEN),
                FocusRatingRequest(skill_id=skill_id, rating=MeetingRating.YELLOW),
            ]
        )
