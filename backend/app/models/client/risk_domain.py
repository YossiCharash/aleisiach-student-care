from enum import StrEnum


class RiskDomain(StrEnum):
    EATING_DRINKING_SWALLOWING = "eating_drinking_swallowing"
    WEIGHT = "weight"
    CHRONIC_CONDITIONS = "chronic_conditions"
    MEDICAL_TREATMENT_REFUSAL = "medical_treatment_refusal"
    INSTABILITY = "instability"
    ESCAPING_WANDERING = "escaping_wandering"
    HARM = "harm"
    COMPULSIVE_BEHAVIOR = "compulsive_behavior"
    SEXUAL_SOCIAL_RISK = "sexual_social_risk"
    VICTIM_BEHAVIOR = "victim_behavior"
    COMMUNITY_MOBILITY = "community_mobility"
    ORIENTATION_TRANSPORT = "orientation_transport"
    STAYING_HOME_ALONE = "staying_home_alone"
    CENTER_UNSUPERVISED = "center_unsupervised"
    INDEPENDENT_MEDICATION = "independent_medication"
    CLEANING_SHARP_TOOLS = "cleaning_sharp_tools"
    LEAVING_CENTER_ALONE = "leaving_center_alone"
