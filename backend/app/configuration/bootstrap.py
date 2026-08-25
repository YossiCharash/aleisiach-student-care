from backend.app.client.database.database import Database
from backend.app.client.email.console_email_sender import ConsoleEmailSender
from backend.app.client.email.email_sender import EmailSender
from backend.app.configuration.settings import Settings
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory


class Bootstrap:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(settings.database)
        self.password_hasher = PasswordHasher()
        self.token_factory = TokenFactory()
        self.email_sender: EmailSender = ConsoleEmailSender()
