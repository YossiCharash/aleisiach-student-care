import json
import logging
import urllib.request

from backend.app.client.whatsapp.whatsapp_notifier import WhatsAppNotifier
from backend.app.configuration.notifications.whatsapp_settings import WhatsAppSettings
from backend.app.schema.service.error_alert import ErrorAlert

logger = logging.getLogger("backend.app.whatsapp")


class WebhookWhatsAppNotifier(WhatsAppNotifier):
    def __init__(self, settings: WhatsAppSettings) -> None:
        self._settings = settings

    def notify(self, alert: ErrorAlert) -> None:
        if not self._settings.webhook_url:
            logger.warning("WhatsApp webhook URL not configured; dropped alert %s", alert.reference)
            return
        try:
            self._post(self.build_payload(alert))
        except Exception:
            logger.exception("Failed to deliver WhatsApp alert %s", alert.reference)

    def build_payload(self, alert: ErrorAlert) -> dict[str, object]:
        return {
            "recipient": self._settings.recipient,
            "text": self.format_text(alert),
            "alert": alert.model_dump(mode="json"),
        }

    def _post(self, payload: dict[str, object]) -> None:
        request = urllib.request.Request(
            self._settings.webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self._settings.webhook_timeout_seconds):
            return
