from backend.app.client.pdf.pdf_renderer import PdfRenderer

_DATA_ONLY_PROTOCOLS = frozenset({"data"})


def _data_only_url_fetcher(url: str) -> object:
    if not url.startswith("data:"):
        raise ValueError("PDF rendering may only resolve data: URIs")
    from weasyprint.urls import URLFetcher

    return URLFetcher(allowed_protocols=_DATA_ONLY_PROTOCOLS).fetch(url)


class WeasyPrintPdfRenderer(PdfRenderer):
    def render(self, html: str) -> bytes:
        from weasyprint import HTML
        from weasyprint.urls import URLFetcher

        fetcher = URLFetcher(allowed_protocols=_DATA_ONLY_PROTOCOLS)
        document = HTML(string=html, url_fetcher=fetcher)
        return bytes(document.write_pdf())
