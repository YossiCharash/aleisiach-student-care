from enum import StrEnum


class IncidentNature(StrEnum):
    ACCIDENT_INJURY_DEATH = "accident_injury_death"
    VIOLENCE = "violence"
    PROPERTY_DAMAGE = "property_damage"
    PROHIBITED_SUBSTANCES = "prohibited_substances"
    OTHER = "other"
