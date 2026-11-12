from types import MappingProxyType

from backend.app.models.client.work_style import WorkStyle

WORK_STYLE_LABELS: MappingProxyType[WorkStyle, str] = MappingProxyType(
    {
        WorkStyle.INDIVIDUAL: "אישי",
        WorkStyle.GROUP: "קבוצתי",
    }
)
