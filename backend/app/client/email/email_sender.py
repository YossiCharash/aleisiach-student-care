from abc import ABC, abstractmethod

from backend.app.schema.service.password_reset_message import PasswordResetMessage


class EmailSender(ABC):
    @abstractmethod
    def send_invitation(self, email: str, link: str) -> None: ...

    @abstractmethod
    def send_password_reset(self, message: PasswordResetMessage) -> None: ...
