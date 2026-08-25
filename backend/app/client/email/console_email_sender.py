import logging

from backend.app.client.email.email_sender import EmailSender

logger = logging.getLogger("backend.app.email")


class ConsoleEmailSender(EmailSender):
    def send_invitation(self, email: str, link: str) -> None:
        logger.info("Invitation email to %s: %s", email, link)

    def send_password_reset(self, email: str, link: str) -> None:
        logger.info("Password reset email to %s: %s", email, link)
