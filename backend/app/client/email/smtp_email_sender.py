import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from backend.app.client.email.email_sender import EmailSender
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.schema.service.password_reset_message import PasswordResetMessage

_INVITE_SUBJECT = "הזמנה למערכת עלי שיח"
_RESET_SUBJECT = "איפוס סיסמה — עלי שיח"


class SmtpEmailSender(EmailSender):
    def __init__(self, settings: EmailSettings) -> None:
        self._settings = settings

    def send_invitation(self, email: str, link: str) -> None:
        body = f"הוזמנת למערכת עלי שיח. להשלמת ההרשמה: {link}"
        self._deliver(self._message(email, _INVITE_SUBJECT, body))

    def send_password_reset(self, message: PasswordResetMessage) -> None:
        account = f"{message.username} · {message.institution_name}"
        body = f"התקבלה בקשה לאיפוס סיסמה עבור החשבון {account}. לאיפוס: {message.link}"
        self._deliver(self._message(message.email, _RESET_SUBJECT, body))

    def _message(self, to: str, subject: str, body: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self._settings.from_address
        message["To"] = to
        message["Subject"] = subject
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid(domain=self._sender_domain())
        message.set_content(body)
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
