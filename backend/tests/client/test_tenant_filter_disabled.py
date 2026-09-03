from backend.app.client.database.tenant_filter import TenantFilter
from backend.tests.support.tenant_filter_disabled import tenant_filter_disabled


def test_the_filter_is_off_inside_the_block_and_back_on_after() -> None:
    with tenant_filter_disabled():
        assert not TenantFilter.is_registered()

    assert TenantFilter.is_registered()


def test_the_filter_is_restored_even_when_the_block_raises() -> None:
    try:
        with tenant_filter_disabled():
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    assert TenantFilter.is_registered()
