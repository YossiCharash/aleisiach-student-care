from types import MappingProxyType

MEDICAL_SUMMARY_OPTIONS: MappingProxyType[str, tuple[tuple[str, str], ...]] = MappingProxyType(
    {
        "lives_with": (
            ("community_housing", "דיור בקהילה"),
            ("parents", "עם ההורים"),
            ("alone", "לבד"),
            ("partner", "עם בן/בת זוג"),
        ),
        "dental_treatment": (
            ("unknown", "לא ידוע"),
            ("follow_up", "במעקב"),
            ("needs_rehabilitation", "זקוק לשיקום פה"),
        ),
        "dentures": (
            ("fixed", "קבועות"),
            ("implants", "שתלים"),
            ("removable", "תותבת"),
        ),
        "skin_integrity": (
            ("intact", "תקין"),
            ("not_intact", "לא תקין"),
        ),
        "comprehension": (
            ("complex_instructions", "מבין הוראות מורכבות"),
            ("simple_instructions", "מבין הוראות פשוטות"),
            ("gestures", "מבין ג׳סטות והדגמות ללא מילים"),
            ("none", "אין הבנה מתאימה להוראות"),
        ),
        "communication": (
            ("independent", "מתבטא באופן עצמאי וברור"),
            ("single_words", "מתבטא במילים בודדות"),
            ("alternative", "מתקשר בתקשורת חליפית (פלט / לוח / אחר)"),
        ),
        "speech": (
            ("clear", "דיבורו ברור"),
            ("articulation", "יש הפרעות היגוי עקביות"),
            ("unclear", "דיבורו מסורבל וקשה להבינו"),
            ("nonverbal", "אינו מדבר"),
            ("gestures", "משתמש בתנועות ידיים וג׳סטות"),
        ),
        "vision": (
            ("normal", "תקינה"),
            ("impaired", "ידוע על ליקוי ראייה"),
            ("glasses_distance", "מרכיב משקפיים לראייה מרחוק"),
            ("glasses_near", "מרכיב משקפיים לראייה מקרוב"),
        ),
        "hearing": (
            ("normal", "תקינה"),
            ("impaired", "ידוע על ליקוי שמיעה"),
            ("aid_left", "מרכיב מכשיר שמיעה באוזן שמאל"),
            ("aid_right", "מרכיב מכשיר שמיעה באוזן ימין"),
            ("aid_both", "מרכיב מכשיר שמיעה בשתי אוזניים"),
        ),
        "functioning": (
            ("independent", "עצמאי"),
            ("light_help", "זקוק לסיוע קל בפעולות בודדות"),
            ("ongoing_help", "זקוק לסיוע בפעולות לאורך זמן"),
            ("dependent", "תלוי בזולת בכל פעולותיו"),
        ),
        "mobility": (
            ("independent", "עצמאי"),
            ("escort", "זקוק לליווי"),
            ("close_escort", "זקוק למלווה צמוד"),
            ("position_change", "זקוק לסיוע בשינוי תנוחות"),
            ("aids", "משתמש בעזרים (הליכון, כסא גלגלים, קביים)"),
        ),
        "eating": (
            ("independent", "עצמאי"),
            ("light_support", "זקוק לתמיכה קלה"),
            ("maximal_support", "זקוק לתמיכה מרבית"),
        ),
        "chewing_swallowing": (
            ("no_chewing_difficulty", "אין קושי בלעיסה"),
            ("no_swallowing_difficulty", "אין קושי בבליעה"),
        ),
        "food_texture": (
            ("not_needed", "אין צורך"),
            ("chopped", "מזון גרוס"),
            ("minced", "מזון טחון"),
            ("thickened_liquids", "הסמכת נוזלים"),
        ),
        "diet": (
            ("regular", "רגילה"),
            ("low_fat", "דלת שומן"),
            ("low_sugar", "דלת סוכר"),
            ("other", "אחר"),
        ),
        "continence": (
            ("full", "מלאה"),
            ("partial", "חלקית"),
            ("pull_ups", "שימוש במכנסונים"),
            ("diapers", "שימוש בפנרוס"),
            ("catheter_temporary", "שימוש בקטטר זמני"),
            ("catheter_permanent", "שימוש בקטטר קבוע"),
        ),
    }
)
