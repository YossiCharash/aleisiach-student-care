from abc import ABC, abstractmethod

from backend.app.schema.service.error_alert import ErrorAlert


class WhatsAppNotifier(ABC):
    @abstractmethod
    def notify(self, alert: ErrorAlert) -> None: ...

    @staticmethod
    def format_text(alert: ErrorAlert) -> str:
        occurred_at = alert.occurred_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        lines = [
            "🚨 שגיאה במערכת עלי שיח",
            f"סביבה: {alert.environment}",
            f"מזהה תקלה: {alert.reference}",
            f"בקשה: {alert.method} {alert.path}",
            f"סוג: {alert.error_type}",
            f"פירוט: {alert.message}",
            f"זמן: {occurred_at}",
        ]
        return "\n".join(lines)
