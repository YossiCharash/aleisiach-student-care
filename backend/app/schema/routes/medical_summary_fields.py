from datetime import date

from pydantic import BaseModel, Field

_MAX_TEXT = 5000
_MAX_SHORT = 300


class MedicalSummaryFields(BaseModel):
    phone: str = Field(default="", max_length=_MAX_SHORT)
    lives_with: list[str] = Field(default_factory=list)
    allergies: str = Field(default="", max_length=_MAX_TEXT)
    known_syndrome: str = Field(default="", max_length=_MAX_TEXT)
    background_diseases: str = Field(default="", max_length=_MAX_TEXT)
    hospitalizations_surgeries: str = Field(default="", max_length=_MAX_TEXT)
    dental_treatment: list[str] = Field(default_factory=list)
    dentures: list[str] = Field(default_factory=list)
    epilepsy_known: bool | None = None
    epilepsy_seizure_nature: str = Field(default="", max_length=_MAX_TEXT)
    epilepsy_seizure_frequency: str = Field(default="", max_length=_MAX_SHORT)
    epilepsy_last_seizure: date | None = None
    epilepsy_seizure_treatment: str = Field(default="", max_length=_MAX_TEXT)
    dual_diagnosis_known: bool | None = None
    dual_diagnosis_expression: str = Field(default="", max_length=_MAX_TEXT)
    dual_diagnosis_frequency: str = Field(default="", max_length=_MAX_SHORT)
    dual_diagnosis_treatment: str = Field(default="", max_length=_MAX_TEXT)
    skin_integrity: list[str] = Field(default_factory=list)
    skin_known_issues: str = Field(default="", max_length=_MAX_TEXT)
    comprehension: list[str] = Field(default_factory=list)
    communication: list[str] = Field(default_factory=list)
    communication_other: str = Field(default="", max_length=_MAX_SHORT)
    speech: list[str] = Field(default_factory=list)
    vision: list[str] = Field(default_factory=list)
    hearing: list[str] = Field(default_factory=list)
    functioning: list[str] = Field(default_factory=list)
    mobility: list[str] = Field(default_factory=list)
    eating: list[str] = Field(default_factory=list)
    gastrostomy_feeding: bool | None = None
    formula: str = Field(default="", max_length=_MAX_SHORT)
    chewing_swallowing: list[str] = Field(default_factory=list)
    food_texture: list[str] = Field(default_factory=list)
    diet: list[str] = Field(default_factory=list)
    diet_other: str = Field(default="", max_length=_MAX_SHORT)
    continence: list[str] = Field(default_factory=list)
    loves: str = Field(default="", max_length=_MAX_TEXT)
    calming: str = Field(default="", max_length=_MAX_TEXT)
    angering: str = Field(default="", max_length=_MAX_TEXT)
    frightening: str = Field(default="", max_length=_MAX_TEXT)
    stress_behavior: str = Field(default="", max_length=_MAX_TEXT)
    care_recommendations: str = Field(default="", max_length=_MAX_TEXT)
    general_notes: str = Field(default="", max_length=_MAX_TEXT)
    guardian_name: str = Field(default="", max_length=_MAX_SHORT)
    guardian_relation: str = Field(default="", max_length=_MAX_SHORT)
    guardian_phone: str = Field(default="", max_length=_MAX_SHORT)
    health_fund: str = Field(default="", max_length=_MAX_SHORT)
    supplemental_insurance: bool | None = None
    supplemental_insurance_detail: str = Field(default="", max_length=_MAX_SHORT)
    attending_doctor: str = Field(default="", max_length=_MAX_SHORT)
    care_nurse: str = Field(default="", max_length=_MAX_SHORT)
    community_social_worker: str = Field(default="", max_length=_MAX_SHORT)
    social_worker_phone: str = Field(default="", max_length=_MAX_SHORT)
    filler_role: str = Field(default="", max_length=_MAX_SHORT)

    @classmethod
    def field_names(cls) -> tuple[str, ...]:
        return tuple(MedicalSummaryFields.model_fields)
