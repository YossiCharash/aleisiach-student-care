from types import MappingProxyType

from backend.app.models.client.health_session_type import HealthSessionType

HEALTH_SESSION_TYPE_LABELS: MappingProxyType[HealthSessionType, str] = MappingProxyType(
    {
        HealthSessionType.INDIVIDUAL: "אישי",
        HealthSessionType.GROUP: "קבוצתי",
    }
)
