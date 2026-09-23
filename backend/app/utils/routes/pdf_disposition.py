from urllib.parse import quote

_ASCII_FALLBACK = "document.pdf"


def pdf_content_disposition(student_name: str, document_label: str) -> str:
    filename = f"{student_name} - {document_label}.pdf"
    encoded = quote(filename, safe="")
    return f"inline; filename=\"{_ASCII_FALLBACK}\"; filename*=UTF-8''{encoded}"
