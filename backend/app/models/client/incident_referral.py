from enum import StrEnum


class IncidentReferral(StrEnum):
    INTERNAL_EVENT = "internal_event"
    GUARDIAN = "guardian"
    WELFARE_SOCIAL_WORKER = "welfare_social_worker"
    STATUTORY_SOCIAL_WORKER = "statutory_social_worker"
    POLICE = "police"
    FRAMEWORK_SUPERVISOR = "framework_supervisor"
    OTHER = "other"
