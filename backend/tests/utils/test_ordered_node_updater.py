from backend.app.models.client.label import Label
from backend.app.schema.routes.ordered_node_update_request import OrderedNodeUpdateRequest
from backend.app.utils.service.ordered_node_updater import OrderedNodeUpdater


def _label() -> Label:
    return Label(name="ניקיון", order=3, is_active=True)


def test_apply_reports_only_the_fields_that_were_sent() -> None:
    node = _label()

    changes = OrderedNodeUpdater.apply(node, OrderedNodeUpdateRequest(name="היגיינה"))

    assert changes == ["name"]
    assert node.name == "היגיינה"
    assert node.order == 3
    assert node.is_active is True


def test_apply_writes_every_field_that_was_sent() -> None:
    node = _label()

    changes = OrderedNodeUpdater.apply(
        node, OrderedNodeUpdateRequest(name="היגיינה", order=0, is_active=False)
    )

    assert changes == ["name", "order", "is_active"]
    assert (node.name, node.order, node.is_active) == ("היגיינה", 0, False)


def test_apply_leaves_an_empty_request_alone() -> None:
    node = _label()

    assert OrderedNodeUpdater.apply(node, OrderedNodeUpdateRequest()) == []
    assert (node.name, node.order, node.is_active) == ("ניקיון", 3, True)


def test_a_deactivating_request_is_not_mistaken_for_an_absent_field() -> None:
    node = _label()

    changes = OrderedNodeUpdater.apply(node, OrderedNodeUpdateRequest(is_active=False))

    assert changes == ["is_active"]
    assert node.is_active is False


def test_the_request_trims_the_name() -> None:
    assert OrderedNodeUpdateRequest(name="  היגיינה  ").name == "היגיינה"
