import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from backend.app.client.email.branded_email_renderer import BrandedEmailRenderer
from backend.app.client.email.email_sender import EmailSender
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.schema.client.email.rendered_email import RenderedEmail
from backend.app.schema.service.password_reset_message import PasswordResetMessage


class SmtpEmailSender(EmailSender):
    def __init__(self, settings: EmailSettings) -> None:
        self._settings = settings
        self._renderer = BrandedEmailRenderer(settings)

    def send_invitation(self, email: str, link: str) -> None:
        self._deliver(self._message(email, self._renderer.invitation(link)))

    def send_password_reset(self, message: PasswordResetMessage) -> None:
        rendered = self._renderer.password_reset(message)
        self._deliver(self._message(message.email, rendered))

    def _message(self, to: str, rendered: RenderedEmail) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self._settings.from_address
        message["To"] = to
        message["Subject"] = rendered.subject
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid(domain=self._sender_domain())
        message["Auto-Submitted"] = "auto-generated"
        message.set_content(rendered.text_body)
        message.add_alternative(rendered.html_body, subtype="html")
        return message

    def _sender_domain(self) -> str:
        _, _, domain = self._settings.from_address.rpartition("@")
        return domain or self._settings.smtp_host

    def _deliver(self, message: EmailMessage) -> None:
        with smtplib.SMTP(
            self._settings.smtp_host,
            self._settings.smtp_port,
            timeout=self._settings.smtp_timeout_seconds,
        ) as smtp:
            if self._settings.smtp_starttls:
                smtp.starttls(context=ssl.create_default_context())
            if self._settings.smtp_username:
                smtp.login(self._settings.smtp_username, self._settings.smtp_password)
            smtp.send_message(message)
