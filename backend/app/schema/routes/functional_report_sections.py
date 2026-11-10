from pydantic import BaseModel, Field

_MAX_SECTION = 5000


class FunctionalReportSections(BaseModel):
    general_background: str = Field(default="", max_length=_MAX_SECTION)
    vocational_domain: str = Field(default="", max_length=_MAX_SECTION)
    behavioral_emotional_domain: str = Field(default="", max_length=_MAX_SECTION)
    communication_social_domain: str = Field(default="", max_length=_MAX_SECTION)
    independence_life_skills_domain: str = Field(default="", max_length=_MAX_SECTION)
    summary_recommendations: str = Field(default="", max_length=_MAX_SECTION)

    @classmethod
    def section_names(cls) -> tuple[str, ...]:
        return tuple(FunctionalReportSections.model_fields)
