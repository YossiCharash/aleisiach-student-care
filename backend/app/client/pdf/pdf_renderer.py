from abc import ABC, abstractmethod


class PdfRenderer(ABC):
    @abstractmethod
    def render(self, html: str) -> bytes: ...
