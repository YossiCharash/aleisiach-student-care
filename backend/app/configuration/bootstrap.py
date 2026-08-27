from backend.app.client.database.database import Database
from backend.app.client.email.console_email_sender import ConsoleEmailSender
from backend.app.client.email.email_sender import EmailSender
from backend.app.client.email.smtp_email_sender import SmtpEmailSender
from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.client.pdf.weasyprint_pdf_renderer import WeasyPrintPdfRenderer
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.configuration.settings import Settings
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

    @staticmethod
    def _build_email_sender(email_settings: EmailSettings) -> EmailSender:
        if email_settings.provider == "smtp":
            return SmtpEmailSender(email_settings)
        return ConsoleEmailSender()
