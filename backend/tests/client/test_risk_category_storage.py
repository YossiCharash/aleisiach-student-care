from collections.abc import Iterator

import pytest
from sqlalchemy import Column, Integer, MetaData, Table, create_engine, insert, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    yield engine
    engine.dispose()


def _probe_table() -> tuple[MetaData, Table]:
    metadata = MetaData()
    table = Table(
        "risk_category_probe",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("category", RiskDomain.__table__.c.category.type, nullable=False),
    )
    return metadata, table


def test_seeded_lowercase_category_is_readable(engine: Engine) -> None:
    metadata, table = _probe_table()
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO risk_category_probe (id, category) VALUES (1, 'medical')")
        )
        loaded = connection.execute(select(table.c.category)).scalar_one()
    assert loaded is RiskCategory.MEDICAL


def test_category_is_stored_by_value(engine: Engine) -> None:
    metadata, table = _probe_table()
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(insert(table).values(id=1, category=RiskCategory.BEHAVIORAL))
        raw = connection.execute(text("SELECT category FROM risk_category_probe")).scalar_one()
    assert raw == "behavioral"
