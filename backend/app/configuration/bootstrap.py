from backend.app.client.database.database import Database
from backend.app.client.email.console_email_sender import ConsoleEmailSender
from backend.app.client.email.email_sender import EmailSender
from backend.app.client.email.smtp_email_sender import SmtpEmailSender
from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.client.pdf.weasyprint_pdf_renderer import WeasyPrintPdfRenderer
from backend.app.client.whatsapp.console_whatsapp_notifier import ConsoleWhatsAppNotifier
from backend.app.client.whatsapp.webhook_whatsapp_notifier import WebhookWhatsAppNotifier
from backend.app.client.whatsapp.whatsapp_notifier import WhatsAppNotifier
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.configuration.notifications.whatsapp_settings import WhatsAppSettings
from backend.app.configuration.settings import Settings
from backend.app.service.alerts.error_alert_service import ErrorAlertService
from backend.app.utils.service.clock import Clock
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory


class Bootstrap:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(settings.database)
        self.password_hasher = PasswordHasher()
        self.token_factory = TokenFactory()
        self.clock = Clock()
        self.email_sender: EmailSender = self._build_email_sender(settings.email)
        self.pdf_renderer: PdfRenderer = WeasyPrintPdfRenderer()
        self.whatsapp_notifier: WhatsAppNotifier = self._build_whatsapp_notifier(settings.whatsapp)
        self.error_alert_service = ErrorAlertService(
            notifier=self.whatsapp_notifier,
            clock=self.clock,
            environment=settings.app.environment,
            enabled=settings.whatsapp.enabled,
            message_max_length=settings.whatsapp.message_max_length,
        )

    @staticmethod
    def _build_email_sender(email_settings: EmailSettings) -> EmailSender:
        if email_settings.provider == "smtp":
            return SmtpEmailSender(email_settings)
        return ConsoleEmailSender()

    @staticmethod
    def _build_whatsapp_notifier(settings: WhatsAppSettings) -> WhatsAppNotifier:
        if settings.provider == "webhook":
            return WebhookWhatsAppNotifier(settings)
        return ConsoleWhatsAppNotifier()
