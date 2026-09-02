import smtplib
import ssl
from email.message import EmailMessage

from backend.app.client.email.email_sender import EmailSender
from backend.app.configuration.email.email_settings import EmailSettings

_INVITE_SUBJECT = "הזמנה למערכת עלי שיח"
_RESET_SUBJECT = "איפוס סיסמה — עלי שיח"


class SmtpEmailSender(EmailSender):
    def __init__(self, settings: EmailSettings) -> None:
        self._settings = settings

    def send_invitation(self, email: str, link: str) -> None:
        body = f"הוזמנת למערכת עלי שיח. להשלמת ההרשמה: {link}"
        self._deliver(self._message(email, _INVITE_SUBJECT, body))

    def send_password_reset(self, email: str, link: str) -> None:
        body = f"התקבלה בקשה לאיפוס סיסמה. לאיפוס: {link}"
        self._deliver(self._message(email, _RESET_SUBJECT, body))

    def _message(self, to: str, subject: str, body: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self._settings.from_address
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        return message

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
