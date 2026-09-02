from enum import StrEnum


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    ARCHIVE = "archive"
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    LOCKOUT = "lockout"
    PASSWORD_RESET = "password_reset"
    PASSWORD_CHANGE = "password_change"
    INVITATION_ACCEPTED = "invitation_accepted"
