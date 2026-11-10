from types import MappingProxyType

from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_domain import RiskDomain
from backend.app.models.client.risk_level import RiskLevel

RISK_CATEGORY_LABELS: MappingProxyType[RiskCategory, str] = MappingProxyType(
    {
        RiskCategory.MEDICAL: "רפואי",
        RiskCategory.BEHAVIORAL: "התנהגותי",
        RiskCategory.INDEPENDENCE: "עצמאות",
    }
)

RISK_LEVEL_LABELS: MappingProxyType[RiskLevel, str] = MappingProxyType(
    {
        RiskLevel.LOW: "נמוך",
        RiskLevel.MEDIUM: "בינוני",
        RiskLevel.HIGH: "גבוה",
        RiskLevel.NOT_RELEVANT: "לא רלוונטי",
    }
)

RISK_DOMAIN_CATALOG: tuple[tuple[RiskDomain, RiskCategory, str], ...] = (
    (
        RiskDomain.EATING_DRINKING_SWALLOWING,
        RiskCategory.MEDICAL,
        "אכילה, שתיה ובליעה (חנק, חסר שיניים, קצב מהיר, מזון מרוסק, חטיפת אוכל, שתיה, "
        "רגישויות, אלרגיות)",
    ),
    (RiskDomain.WEIGHT, RiskCategory.MEDICAL, "עודף / חוסר משקל"),
    (RiskDomain.CHRONIC_CONDITIONS, RiskCategory.MEDICAL, "אפילפסיה / סוכרת / אסטמה"),
    (
        RiskDomain.MEDICAL_TREATMENT_REFUSAL,
        RiskCategory.MEDICAL,
        "סרבנות לטיפול רפואי (תרופות, בדיקות דם, ביקור רופא וכו׳)",
    ),
    (RiskDomain.INSTABILITY, RiskCategory.MEDICAL, "אי יציבות (נפילות, נעליים מיוחדות)"),
    (RiskDomain.ESCAPING_WANDERING, RiskCategory.BEHAVIORAL, "בריחות ו/או שוטטות"),
    (RiskDomain.HARM, RiskCategory.BEHAVIORAL, "פגיעה עצמית / פגיעה בסביבה / פגיעה ברכוש"),
    (RiskDomain.COMPULSIVE_BEHAVIOR, RiskCategory.BEHAVIORAL, "התנהגות כפייתית"),
    (
        RiskDomain.SEXUAL_SOCIAL_RISK,
        RiskCategory.BEHAVIORAL,
        "סיכון בתחום המיני-חברתי (פוגע / נפגע)",
    ),
    (RiskDomain.VICTIM_BEHAVIOR, RiskCategory.BEHAVIORAL, "התנהגות קרבנית"),
    (RiskDomain.COMMUNITY_MOBILITY, RiskCategory.INDEPENDENCE, "ניידות בקהילה"),
    (
        RiskDomain.ORIENTATION_TRANSPORT,
        RiskCategory.INDEPENDENCE,
        "התמצאות במרחב, שימוש בתחבורה, חצית כבישים",
    ),
    (RiskDomain.STAYING_HOME_ALONE, RiskCategory.INDEPENDENCE, "השארות בדירה באופן עצמאי"),
    (
        RiskDomain.CENTER_UNSUPERVISED,
        RiskCategory.INDEPENDENCE,
        "שהות ברחבי המרכז ללא השגחה צמודה",
    ),
    (RiskDomain.INDEPENDENT_MEDICATION, RiskCategory.INDEPENDENCE, "לקיחת תרופות באופן עצמאי"),
    (
        RiskDomain.CLEANING_SHARP_TOOLS,
        RiskCategory.INDEPENDENCE,
        "שימוש בחומרי ניקוי וכלי מטבח חדים",
    ),
    (RiskDomain.LEAVING_CENTER_ALONE, RiskCategory.INDEPENDENCE, "סיכון ביציאה עצמאית מהמרכז"),
)
