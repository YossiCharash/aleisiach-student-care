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
    ) -> None:
        self._notifier = notifier
        self._clock = clock
        self._environment = environment
        self._enabled = enabled

    def report(
        self, error: Exception, method: str, path: str, institution: str | None = None
    ) -> str:
        reference = uuid.uuid4().hex[:12]
        logger.error("Unhandled error %s on %s %s", reference, method, path, exc_info=error)
        if self._enabled:
            self._dispatch(self._build_alert(error, method, path, reference, institution))
        return reference

    def _build_alert(
        self,
        error: Exception,
        method: str,
        path: str,
        reference: str,
        institution: str | None,
    ) -> ErrorAlert:
        return ErrorAlert(
            reference=reference,
            error_type=type(error).__name__,
            method=method,
            path=path,
            environment=self._environment,
            institution=institution,
            occurred_at=self._clock.now(),
        )

    def _dispatch(self, alert: ErrorAlert) -> None:
        try:
            self._notifier.notify(alert)
        except Exception:
            logger.exception("WhatsApp notifier failed for alert %s", alert.reference)
