from typing import Protocol


class UrlFetcher(Protocol):
    def fetch(self, url: str) -> object: ...
