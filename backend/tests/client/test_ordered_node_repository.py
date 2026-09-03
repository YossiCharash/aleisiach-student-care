from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label


def test_next_order_continues_after_the_existing_nodes(db_session: Session) -> None:
    repository = TaxonomyRepository(db_session)
    repository.add_label(Label(name="ניקיון", order=repository.next_label_order()))
    repository.add_label(Label(name="תזונה", order=repository.next_label_order()))

    assert repository.next_label_order() == 2


def test_next_order_ignores_the_nodes_of_another_institution(
    db_session: Session, seed_institution: Callable[..., Institution]
) -> None:
    repository = TaxonomyRepository(db_session)
    repository.add_label(Label(name="ניקיון", order=0))
    repository.add_label(Label(name="תזונה", order=1))
    neighbour = seed_institution("מוסד שכן", "neighbour")

    TenantBinding.bind(db_session, neighbour.id)

    assert repository.next_label_order() == 0


def test_next_order_refuses_to_answer_without_a_bound_institution(db_session: Session) -> None:
    repository = TaxonomyRepository(db_session)

    with TenantBinding.platform(db_session), pytest.raises(AuthorizationError):
        repository.next_label_order()
