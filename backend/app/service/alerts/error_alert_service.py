import logging
import uuid

from backend.app.client.whatsapp.whatsapp_notifier import WhatsAppNotifier
from backend.app.schema.service.error_alert import ErrorAlert
from backend.app.utils.service.clock import Clock

logger = logging.getLogger("backend.app.errors")


class ErrorAlertService:
    def __init__(
        self,
        notifier: WhatsAppNotifier,
        clock: Clock,
        environment: str,
        enabled: bool,
        message_max_length: int,
    ) -> None:
        self._notifier = notifier
        self._clock = clock
        self._environment = environment
        self._enabled = enabled
        self._message_max_length = message_max_length

    def report(self, error: Exception, method: str, path: str) -> str:
        reference = uuid.uuid4().hex[:12]
        logger.error("Unhandled error %s on %s %s", reference, method, path, exc_info=error)
        if self._enabled:
            self._dispatch(self._build_alert(error, method, path, reference))
        return reference

    def _build_alert(self, error: Exception, method: str, path: str, reference: str) -> ErrorAlert:
        return ErrorAlert(
            reference=reference,
            error_type=type(error).__name__,
            message=self._truncate(str(error) or type(error).__name__),
            method=method,
            path=path,
            environment=self._environment,
            occurred_at=self._clock.now(),
        )

    def _dispatch(self, alert: ErrorAlert) -> None:
        try:
            self._notifier.notify(alert)
        except Exception:
            logger.exception("WhatsApp notifier failed for alert %s", alert.reference)

    def _truncate(self, text: str) -> str:
        if len(text) <= self._message_max_length:
            return text
        return text[: self._message_max_length - 1] + "…"
