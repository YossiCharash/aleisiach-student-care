from collections.abc import Iterator

import pytest
from sqlalchemy import Column, Enum, Integer, MetaData, Table, create_engine, insert, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from backend.app.models.client.meeting_foci_entry import MeetingFociEntry
from backend.app.models.client.meeting_plan_entry import MeetingPlanEntry
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program_entry import ProgramEntry
from backend.app.models.client.program_plan_entry import ProgramPlanEntry
from backend.app.models.client.solution import Solution

_RATING_COLUMNS = (
    Solution.__table__.c.rating,
    ProgramEntry.__table__.c.rating,
    ProgramPlanEntry.__table__.c.rating,
    MeetingFociEntry.__table__.c.rating,
    MeetingPlanEntry.__table__.c.rating,
)


@pytest.mark.parametrize("column", _RATING_COLUMNS)
def test_rating_columns_store_by_member_name(column: Column[MeetingRating]) -> None:
    rating_type = column.type
    assert isinstance(rating_type, Enum)
    assert rating_type.enum_class is MeetingRating
    assert rating_type.values_callable is None


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    yield engine
    engine.dispose()


def _probe_table() -> tuple[MetaData, Table]:
    metadata = MetaData()
    table = Table(
        "rating_probe",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("rating", Enum(MeetingRating, native_enum=False, length=16), nullable=False),
    )
    return metadata, table


def test_rating_round_trips_and_is_stored_uppercase(engine: Engine) -> None:
    metadata, table = _probe_table()
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(insert(table).values(id=1, rating=MeetingRating.YELLOW))
        loaded = connection.execute(select(table.c.rating)).scalar_one()
        raw = connection.execute(text("SELECT rating FROM rating_probe")).scalar_one()
    assert loaded is MeetingRating.YELLOW
    assert raw == "YELLOW"


def test_lowercase_rating_value_cannot_be_read(engine: Engine) -> None:
    metadata, table = _probe_table()
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO rating_probe (id, rating) VALUES (:id, :rating)"),
            {"id": 1, "rating": MeetingRating.YELLOW.value},
        )
        with pytest.raises(LookupError):
            connection.execute(select(table.c.rating)).scalar_one()
