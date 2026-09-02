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


def _service(notifier: WhatsAppNotifier, enabled: bool = True) -> ErrorAlertService:
    return ErrorAlertService(
        notifier=notifier,
        clock=Clock(),
        environment="test",
        enabled=enabled,
    )


def test_report_returns_reference_and_dispatches_alert() -> None:
    notifier = _CapturingNotifier()

    reference = _service(notifier).report(ValueError("bad input"), "POST", "/students")

    assert reference
    assert len(notifier.alerts) == 1
    alert = notifier.alerts[0]
    assert alert.reference == reference
    assert alert.error_type == "ValueError"
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


def test_alert_carries_no_free_text_exception_detail() -> None:
    notifier = _CapturingNotifier()
    secret = "123456789"

    _service(notifier).report(ValueError(f"national id {secret}"), "POST", "/students")

    dumped = notifier.alerts[0].model_dump_json()
    assert secret not in dumped
    assert "message" not in notifier.alerts[0].model_dump()


def test_alert_carries_the_institution_code() -> None:
    notifier = _CapturingNotifier()

    _service(notifier).report(RuntimeError("boom"), "GET", "/students", "sharon")

    assert notifier.alerts[0].institution == "sharon"
    assert "sharon" in WhatsAppNotifier.format_text(notifier.alerts[0])


def test_alert_omits_the_institution_line_for_platform_requests() -> None:
    notifier = _CapturingNotifier()

    _service(notifier).report(RuntimeError("boom"), "GET", "/institutions")

    assert notifier.alerts[0].institution is None
    assert "מוסד:" not in WhatsAppNotifier.format_text(notifier.alerts[0])
