from datetime import date, datetime

from backend.app.utils.service.clock import Clock


class FakeClock(Clock):
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def now(self) -> datetime:
        return self.moment

    def today(self) -> date:
        return self.moment.date()
