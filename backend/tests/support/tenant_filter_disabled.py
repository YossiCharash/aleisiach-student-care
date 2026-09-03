from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import event
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_filter import TenantFilter


@contextmanager
def tenant_filter_disabled() -> Iterator[None]:
    TenantFilter.register()
    event.remove(Session, "do_orm_execute", TenantFilter._restrict_reads)
    event.remove(Session, "before_flush", TenantFilter._stamp_writes)
    try:
        yield
    finally:
        TenantFilter.register()
