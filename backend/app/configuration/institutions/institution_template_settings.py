from pydantic import BaseModel, Field

_DETAIL_OPTION_DEFAULTS: dict[str, tuple[str, ...]] = {
    "idd_severity": ("קלה", "בינונית", "מורכבת"),
    "functioning_level": ("נמוך", "בינוני", "גבוה"),
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
    "contact_relationship": ("אבא", "אמא", "אפוטרופוס"),
}

_RISK_DOMAIN_DEFAULTS: tuple[tuple[str, str], ...] = (
    (
        "medical",
        "אכילה, שתיה ובליעה (חנק, חסר שיניים, קצב מהיר, מזון מרוסק, חטיפת אוכל, שתיה, "
        "רגישויות, אלרגיות)",
    ),
    ("medical", "עודף / חוסר משקל"),
    ("medical", "אפילפסיה / סוכרת / אסטמה"),
    ("medical", "סרבנות לטיפול רפואי (תרופות, בדיקות דם, ביקור רופא וכו׳)"),
    ("medical", "אי יציבות (נפילות, נעליים מיוחדות)"),
    ("behavioral", "בריחות ו/או שוטטות"),
    ("behavioral", "פגיעה עצמית / פגיעה בסביבה / פגיעה ברכוש"),
    ("behavioral", "התנהגות כפייתית"),
    ("behavioral", "סיכון בתחום המיני-חברתי (פוגע / נפגע)"),
    ("behavioral", "התנהגות קרבנית"),
    ("independence", "ניידות בקהילה"),
    ("independence", "התמצאות במרחב, שימוש בתחבורה, חצית כבישים"),
    ("independence", "השארות בדירה באופן עצמאי"),
    ("independence", "שהות ברחבי המרכז ללא השגחה צמודה"),
    ("independence", "לקיחת תרופות באופן עצמאי"),
    ("independence", "שימוש בחומרי ניקוי וכלי מטבח חדים"),
    ("independence", "סיכון ביציאה עצמאית מהמרכז"),
)


class InstitutionTemplateSettings(BaseModel):
    detail_options: dict[str, tuple[str, ...]] = Field(
        default_factory=lambda: dict(_DETAIL_OPTION_DEFAULTS)
    )
    risk_domains: tuple[tuple[str, str], ...] = _RISK_DOMAIN_DEFAULTS
