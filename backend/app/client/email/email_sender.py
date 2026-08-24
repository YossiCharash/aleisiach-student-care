from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send_invitation(self, email: str, link: str) -> None: ...

    @abstractmethod
    def send_password_reset(self, email: str, link: str) -> None: ...
