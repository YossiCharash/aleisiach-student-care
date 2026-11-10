from types import MappingProxyType

from backend.app.models.client.risk_category import RiskCategory
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
