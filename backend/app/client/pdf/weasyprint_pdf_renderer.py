from typing import cast

from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.client.pdf.url_fetcher import UrlFetcher

_DATA_ONLY_PROTOCOLS = frozenset({"data"})


def build_data_only_url_fetcher() -> UrlFetcher:
    from weasyprint.urls import URLFetcher

    return cast(UrlFetcher, URLFetcher(allowed_protocols=_DATA_ONLY_PROTOCOLS))


class WeasyPrintPdfRenderer(PdfRenderer):
    def render(self, html: str) -> bytes:
        from weasyprint import HTML

        document = HTML(string=html, url_fetcher=build_data_only_url_fetcher())
        return bytes(document.write_pdf())
