import uuid
from collections.abc import Iterable

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_responsible_user_error import (
    InvalidResponsibleUserError,
)
from backend.app.models.client.student import Student
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.staff_member_response import StaffMemberResponse


class ResponsibleUserResolver:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def candidates(self, student: Student) -> list[StaffMemberResponse]:
        return [
            StaffMemberResponse(id=user.id, full_name=user.full_name)
            for user in self._users.list_all()
            if user.institution_id == student.institution_id and user.status != UserStatus.DISABLED
        ]

    def validate(
        self,
        student: Student,
        user_ids: Iterable[uuid.UUID],
        already_assigned: set[uuid.UUID],
    ) -> dict[uuid.UUID, str | None]:
        names: dict[uuid.UUID, str | None] = {}
        for user_id in user_ids:
            user = self._users.get(user_id)
            if user is None or user.institution_id != student.institution_id:
                raise InvalidResponsibleUserError()
            if user.status == UserStatus.DISABLED and user_id not in already_assigned:
                raise InvalidResponsibleUserError()
            names[user_id] = user.full_name
        return names

    def name(self, user_id: uuid.UUID, cache: dict[uuid.UUID, str | None]) -> str | None:
        if user_id not in cache:
            user = self._users.get(user_id)
            cache[user_id] = user.full_name if user is not None else None
        return cache[user_id]

    def members(
        self, user_ids: Iterable[uuid.UUID], cache: dict[uuid.UUID, str | None]
    ) -> list[StaffMemberResponse]:
        return [
            StaffMemberResponse(id=user_id, full_name=name)
            for user_id in user_ids
            if (name := self.name(user_id, cache)) is not None
        ]
