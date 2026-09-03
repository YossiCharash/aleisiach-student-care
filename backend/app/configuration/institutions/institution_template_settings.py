from pydantic import BaseModel, Field

_DETAIL_OPTION_DEFAULTS: dict[str, tuple[str, ...]] = {
    "idd_severity": ("קלה", "בינונית", "מורכבת"),
    "medication_independence": ("אינו נוטל לבד", "זקוק לתזכורת והשגחה", "עצמאי"),
    "expression_mode": (
        "דיבור מילולי שוטף",
        "מילים בודדות ומשפטים קצרים",
        "ג'סטות ותנועות גוף",
        "שימוש בטאבלט או אייפד",
        "לא ורבלי",
    ),
    "language_comprehension": ("מבין הוראות מורכבות", "מבין רק הוראות פשוטות"),
    "assistive_device": ("משקפיים", "מכשיר שמיעה", "מדרסים", "קביים", "הליכון", "אחר"),
}


class InstitutionTemplateSettings(BaseModel):
    detail_options: dict[str, tuple[str, ...]] = Field(
        default_factory=lambda: dict(_DETAIL_OPTION_DEFAULTS)
    )
