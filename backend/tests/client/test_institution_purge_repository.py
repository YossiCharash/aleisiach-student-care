import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.institutions.institution_purge_repository import (
    InstitutionPurgeRepository,
)
from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.extra_section_type import ExtraSectionType
from backend.app.models.client.institution import Institution
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_session import UserSession
from backend.app.models.client.workshop import Workshop
from backend.app.utils.service.password_hasher import PasswordHasher

_OTHER_INSTITUTION_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def _seed_institution(session: Session) -> uuid.UUID:
    tag = uuid.uuid4().hex[:8]
    institution = Institution(id=uuid.uuid4(), name=f"Inst-{tag}")
    session.add(institution)
    session.flush()
    session.add(Workshop(name=f"W-{tag}", institution_id=institution.id))
    user = User(
        full_name="Member",
        email=f"m-{tag}@example.com",
        username=f"m-{tag}",
        password_hash=PasswordHasher().hash("password123"),
        role=UserRole.MANAGER,
        institution_id=institution.id,
    )
    session.add(user)
    session.flush()
    expires = datetime.now(UTC) + timedelta(days=1)
    session.add(UserSession(user_id=user.id, token_hash=f"s-{tag}", expires_at=expires))
    session.add(
        AuthToken(user_id=user.id, kind=TokenKind.INVITE, token_hash=f"t-{tag}", expires_at=expires)
    )
    parent = ExtraSectionType(name=f"Parent-{tag}", institution_id=institution.id)
    session.add(parent)
    session.flush()
    session.add(
        ExtraSectionType(name=f"Child-{tag}", institution_id=institution.id, parent_id=parent.id)
    )
    session.flush()
    return institution.id


def _count_for(session: Session, institution_id: uuid.UUID) -> dict[str, int]:
    with TenantBinding.platform(session):
        return {
            "users": session.scalar(
                select(func.count()).select_from(User).where(User.institution_id == institution_id)
            )
            or 0,
            "workshops": session.scalar(
                select(func.count())
                .select_from(Workshop)
                .where(Workshop.institution_id == institution_id)
            )
            or 0,
            "sections": session.scalar(
                select(func.count())
                .select_from(ExtraSectionType)
                .where(ExtraSectionType.institution_id == institution_id)
            )
            or 0,
        }


def test_purge_wipes_the_institution_and_its_dependents(db_session: Session) -> None:
    target = _seed_institution(db_session)

    InstitutionPurgeRepository(db_session).purge(target)

    assert db_session.get(Institution, target) is None
    assert _count_for(db_session, target) == {"users": 0, "workshops": 0, "sections": 0}
    assert db_session.scalar(select(func.count()).select_from(UserSession)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuthToken)) == 0


def test_purge_keeps_other_institutions(db_session: Session) -> None:
    kept = _seed_institution(db_session)
    target = _seed_institution(db_session)

    InstitutionPurgeRepository(db_session).purge(target)

    assert db_session.get(Institution, kept) is not None
    assert _count_for(db_session, kept) == {"users": 1, "workshops": 1, "sections": 2}
    assert db_session.get(Institution, _OTHER_INSTITUTION_ID) is not None
