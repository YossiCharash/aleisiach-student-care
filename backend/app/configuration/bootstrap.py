from app.client.database.database import Database
from app.configuration.settings import Settings


class Bootstrap:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(settings.database)
