from backend.app.client.pdf.pdf_renderer import PdfRenderer


class WeasyPrintPdfRenderer(PdfRenderer):
    def render(self, html: str) -> bytes:
        from weasyprint import HTML

        return bytes(HTML(string=html).write_pdf())
