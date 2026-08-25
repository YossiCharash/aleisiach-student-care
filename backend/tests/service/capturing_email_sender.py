from backend.app.client.email.email_sender import EmailSender


class CapturingEmailSender(EmailSender):
    def __init__(self) -> None:
        self.invitation_link: str | None = None
        self.reset_link: str | None = None

    def send_invitation(self, email: str, link: str) -> None:
        self.invitation_link = link

    def send_password_reset(self, email: str, link: str) -> None:
        self.reset_link = link

    @staticmethod
    def token_from(link: str) -> str:
        return link.split("token=", 1)[1]
