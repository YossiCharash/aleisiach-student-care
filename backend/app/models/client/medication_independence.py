from enum import StrEnum


class MedicationIndependence(StrEnum):
    NOT_ALONE = "not_alone"
    NEEDS_REMINDER = "needs_reminder"
    INDEPENDENT = "independent"
