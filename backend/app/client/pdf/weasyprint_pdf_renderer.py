from typing import cast

from backend.app.client.pdf.pdf_renderer import PdfRenderer


def _data_only_url_fetcher(url: str) -> dict[str, object]:
    if not url.startswith("data:"):
        raise ValueError("PDF rendering may only resolve data: URIs")
    from weasyprint import default_url_fetcher

    return cast(dict[str, object], default_url_fetcher(url))


class WeasyPrintPdfRenderer(PdfRenderer):
    def render(self, html: str) -> bytes:
        from weasyprint import HTML

        document = HTML(string=html, url_fetcher=_data_only_url_fetcher)
        return bytes(document.write_pdf())
