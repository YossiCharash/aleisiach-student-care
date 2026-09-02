from backend.app.client.email.email_sender import EmailSender
from backend.app.schema.service.password_reset_message import PasswordResetMessage


class CapturingEmailSender(EmailSender):
    def __init__(self) -> None:
        self.invitation_link: str | None = None
        self.reset_link: str | None = None
        self.reset_messages: list[PasswordResetMessage] = []

    def send_invitation(self, email: str, link: str) -> None:
        self.invitation_link = link

    def send_password_reset(self, message: PasswordResetMessage) -> None:
        self.reset_link = message.link
        self.reset_messages.append(message)

    @staticmethod
    def token_from(link: str) -> str:
        return link.split("token=", 1)[1]
