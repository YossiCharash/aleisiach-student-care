from backend.app.client.whatsapp.whatsapp_notifier import WhatsAppNotifier
from backend.app.schema.service.error_alert import ErrorAlert
from backend.app.service.alerts.error_alert_service import ErrorAlertService
from backend.app.utils.service.clock import Clock


class _CapturingNotifier(WhatsAppNotifier):
    def __init__(self) -> None:
        self.alerts: list[ErrorAlert] = []

    def notify(self, alert: ErrorAlert) -> None:
        self.alerts.append(alert)


class _FailingNotifier(WhatsAppNotifier):
    def notify(self, alert: ErrorAlert) -> None:
        raise RuntimeError("notifier down")


def _service(
    notifier: WhatsAppNotifier, enabled: bool = True, message_max_length: int = 600
) -> ErrorAlertService:
    return ErrorAlertService(
        notifier=notifier,
        clock=Clock(),
        environment="test",
        enabled=enabled,
        message_max_length=message_max_length,
    )


def test_report_returns_reference_and_dispatches_alert() -> None:
    notifier = _CapturingNotifier()

    reference = _service(notifier).report(ValueError("bad input"), "POST", "/students")

    assert reference
    assert len(notifier.alerts) == 1
    alert = notifier.alerts[0]
    assert alert.reference == reference
    assert alert.error_type == "ValueError"
    assert alert.message == "bad input"
    assert alert.method == "POST"
    assert alert.path == "/students"


def test_disabled_service_skips_dispatch() -> None:
    notifier = _CapturingNotifier()

    reference = _service(notifier, enabled=False).report(ValueError("x"), "GET", "/health")

    assert reference
    assert notifier.alerts == []


def test_notifier_failure_does_not_propagate() -> None:
    reference = _service(_FailingNotifier()).report(RuntimeError("x"), "GET", "/health")

    assert reference


def test_message_is_truncated_to_configured_length() -> None:
    notifier = _CapturingNotifier()

    _service(notifier, message_max_length=10).report(RuntimeError("x" * 50), "GET", "/x")

    assert len(notifier.alerts[0].message) == 10
    assert notifier.alerts[0].message.endswith("…")
