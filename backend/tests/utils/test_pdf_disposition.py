from urllib.parse import quote

from backend.app.utils.routes.pdf_disposition import pdf_content_disposition


def test_disposition_encodes_a_hebrew_filename() -> None:
    header = pdf_content_disposition("ישראל ישראלי", "דוח תפקודי")

    expected = quote("ישראל ישראלי - דוח תפקודי.pdf", safe="")
    assert f"filename*=UTF-8''{expected}" in header
    assert header.startswith("inline;")


def test_disposition_keeps_an_ascii_fallback() -> None:
    header = pdf_content_disposition("נועה", "פרטי חניך")

    assert 'filename="document.pdf"' in header
