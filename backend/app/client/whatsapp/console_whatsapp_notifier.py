import logging

from backend.app.client.whatsapp.whatsapp_notifier import WhatsAppNotifier
from backend.app.schema.service.error_alert import ErrorAlert

logger = logging.getLogger("backend.app.whatsapp")


class ConsoleWhatsAppNotifier(WhatsAppNotifier):
    def notify(self, alert: ErrorAlert) -> None:
        logger.info("WhatsApp alert [%s]:\n%s", alert.reference, self.format_text(alert))
