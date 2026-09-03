from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.optional_tenant_scoped import OptionalTenantScoped
from backend.app.models.client.tenant_scoped import TenantScoped

_SCOPED_BASES = (TenantScoped, OptionalTenantScoped)


class TenantFilter:
    @staticmethod
    def register() -> None:
        if TenantFilter.is_registered():
            return
        event.listen(Session, "do_orm_execute", TenantFilter._restrict_reads)
        event.listen(Session, "before_flush", TenantFilter._stamp_writes)

    @staticmethod
    def is_registered() -> bool:
        return event.contains(Session, "do_orm_execute", TenantFilter._restrict_reads)

    @staticmethod
    def _restrict_reads(state: ORMExecuteState) -> None:
        if not state.is_select or state.is_column_load or state.is_relationship_load:
            return
        institution_id = TenantBinding.filter_value(state.session)
        if institution_id is None:
            return
        for base in _SCOPED_BASES:
            state.statement = state.statement.options(
                with_loader_criteria(
                    base,
                    lambda cls: cls.institution_id == institution_id,
                    include_aliases=True,
                )
            )

    @staticmethod
    def _stamp_writes(session: Session, flush_context: object, instances: object) -> None:
        institution_id = TenantBinding.current(session)
        if institution_id is None:
            return
        for instance in session.new:
            if isinstance(instance, TenantScoped) and instance.institution_id is None:
                instance.institution_id = institution_id
