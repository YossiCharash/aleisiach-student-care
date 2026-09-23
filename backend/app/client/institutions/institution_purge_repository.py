import uuid
from typing import Any

from sqlalchemy import Column, ColumnElement, Table, delete, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.base import Base
from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.institution import Institution
from backend.app.models.client.user import User
from backend.app.models.client.user_session import UserSession

_INSTITUTION_COLUMN = "institution_id"


class InstitutionPurgeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def purge(self, institution_id: uuid.UUID) -> None:
        with TenantBinding.platform(self._session):
            self._delete_user_dependents(institution_id)
            for table in reversed(Base.metadata.sorted_tables):
                if table.name == Institution.__tablename__:
                    continue
                if _INSTITUTION_COLUMN not in table.c:
                    continue
                self._delete_scoped_table(table, institution_id)
            self._session.execute(delete(Institution).where(Institution.id == institution_id))
            self._session.flush()

    def _delete_user_dependents(self, institution_id: uuid.UUID) -> None:
        user_ids = select(User.id).where(User.institution_id == institution_id)
        self._session.execute(delete(UserSession).where(UserSession.user_id.in_(user_ids)))
        self._session.execute(delete(AuthToken).where(AuthToken.user_id.in_(user_ids)))

    def _delete_scoped_table(self, table: Table, institution_id: uuid.UUID) -> None:
        scope: ColumnElement[bool] = table.c[_INSTITUTION_COLUMN] == institution_id
        if _is_self_referential(table):
            self._delete_hierarchy(table, scope, institution_id)
            return
        self._session.execute(delete(table).where(scope))

    def _delete_hierarchy(
        self, table: Table, scope: ColumnElement[bool], institution_id: uuid.UUID
    ) -> None:
        parent_column = _self_reference_column(table)
        while True:
            still_parents = (
                select(parent_column)
                .where(table.c[_INSTITUTION_COLUMN] == institution_id)
                .where(parent_column.isnot(None))
            )
            leaf_ids = self._session.scalars(
                select(table.c["id"]).where(scope).where(table.c["id"].notin_(still_parents))
            ).all()
            if not leaf_ids:
                break
            self._session.execute(delete(table).where(table.c["id"].in_(leaf_ids)))


def _is_self_referential(table: Table) -> bool:
    return any(foreign_key.column.table is table for foreign_key in table.foreign_keys)


def _self_reference_column(table: Table) -> Column[Any]:
    for foreign_key in table.foreign_keys:
        if foreign_key.column.table is table and foreign_key.column.name == "id":
            return foreign_key.parent
    raise ValueError(f"no self-referential id column on {table.name}")
