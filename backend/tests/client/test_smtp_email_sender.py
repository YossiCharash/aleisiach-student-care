from email.message import EmailMessage

from backend.app.client.email.console_email_sender import ConsoleEmailSender
from backend.app.client.email.smtp_email_sender import SmtpEmailSender
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.schema.service.password_reset_message import PasswordResetMessage


class _CapturingSmtpSender(SmtpEmailSender):
    def __init__(self, settings: EmailSettings) -> None:
        super().__init__(settings)
        self.sent: list[EmailMessage] = []

    def _deliver(self, message: EmailMessage) -> None:
        self.sent.append(message)


def test_invitation_message_composition() -> None:
    sender = _CapturingSmtpSender(EmailSettings(from_address="no-reply@example.com"))

    sender.send_invitation("user@example.com", "https://app/invite?token=abc123")

    message = sender.sent[0]
    assert message["To"] == "user@example.com"
    assert message["From"] == "no-reply@example.com"
    assert "עלי שיח" in message["Subject"]
    assert "abc123" in message.get_content()


def test_reset_message_composition() -> None:
    sender = _CapturingSmtpSender(EmailSettings())

    sender.send_password_reset(
        PasswordResetMessage(
            email="user@example.com",
            link="https://app/reset?token=xyz789",
            institution_name="מוסד בדיקה",
            username="tester",
        )
    )

    message = sender.sent[0]
    assert "איפוס" in message["Subject"]
    assert "xyz789" in message.get_content()


def test_bootstrap_selects_smtp_when_configured() -> None:
    sender = Bootstrap._build_email_sender(EmailSettings(provider="smtp"))

    assert isinstance(sender, SmtpEmailSender)


def test_bootstrap_defaults_to_console() -> None:
    sender = Bootstrap._build_email_sender(EmailSettings(provider="console"))

    assert isinstance(sender, ConsoleEmailSender)
