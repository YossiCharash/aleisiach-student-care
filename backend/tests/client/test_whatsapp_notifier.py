from datetime import UTC, datetime

from backend.app.client.whatsapp.console_whatsapp_notifier import ConsoleWhatsAppNotifier
from backend.app.client.whatsapp.webhook_whatsapp_notifier import WebhookWhatsAppNotifier
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.notifications.whatsapp_settings import WhatsAppSettings
from backend.app.schema.service.error_alert import ErrorAlert


def _alert() -> ErrorAlert:
    return ErrorAlert(
        reference="abc123",
        error_type="RuntimeError",
        message="boom",
        method="POST",
        path="/students",
        environment="production",
        occurred_at=datetime(2026, 8, 27, 9, 30, tzinfo=UTC),
    )


def test_format_text_contains_reference_and_metadata() -> None:
    text = WebhookWhatsAppNotifier.format_text(_alert())

    assert "abc123" in text
    assert "POST /students" in text
    assert "RuntimeError" in text
    assert "עלי שיח" in text


def test_webhook_payload_wraps_text_and_structured_alert() -> None:
    notifier = WebhookWhatsAppNotifier(
        WhatsAppSettings(webhook_url="https://hook.example/alert", recipient="+972500000000")
    )

    payload = notifier.build_payload(_alert())

    assert payload["recipient"] == "+972500000000"
    assert "abc123" in payload["text"]
    assert payload["alert"]["reference"] == "abc123"


def test_webhook_without_url_does_not_raise() -> None:
    WebhookWhatsAppNotifier(WhatsAppSettings(webhook_url="")).notify(_alert())


def test_webhook_swallows_delivery_failure() -> None:
    class _FailingNotifier(WebhookWhatsAppNotifier):
        def _post(self, payload: dict[str, object]) -> None:
            raise ConnectionError("network down")

    notifier = _FailingNotifier(WhatsAppSettings(webhook_url="https://hook.example/alert"))

    notifier.notify(_alert())


def test_console_notifier_notifies_without_error() -> None:
    ConsoleWhatsAppNotifier().notify(_alert())


def test_bootstrap_selects_webhook_when_configured() -> None:
    notifier = Bootstrap._build_whatsapp_notifier(WhatsAppSettings(provider="webhook"))

    assert isinstance(notifier, WebhookWhatsAppNotifier)


def test_bootstrap_defaults_to_console() -> None:
    notifier = Bootstrap._build_whatsapp_notifier(WhatsAppSettings(provider="console"))

    assert isinstance(notifier, ConsoleWhatsAppNotifier)
