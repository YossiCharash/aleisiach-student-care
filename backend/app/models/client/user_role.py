from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    INSTRUCTOR = "instructor"
    PROFESSIONAL_TEACHER = "professional_teacher"
