from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.utils.service.document_shell import DocumentShell


def _shell(**overrides: str) -> DocumentShell:
    return DocumentShell(BrandSettings(_env_file=None, **overrides))


def test_shell_wraps_the_body_in_an_rtl_hebrew_page() -> None:
    html = _shell().render("", "מוסד בדיקה", "פרטי תלמיד", "<p>גוף</p>")

    assert html.startswith("<!doctype html>")
    assert 'dir="rtl"' in html
    assert 'lang="he"' in html
    assert "<h1>פרטי תלמיד</h1>" in html
    assert "<p>גוף</p>" in html


def test_shell_escapes_the_institution_name() -> None:
    html = _shell().render("", "<script>x</script>", "כותרת", "")

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_base_css_follows_the_configured_brand() -> None:
    html = _shell(primary_color="#123456", text_color="#654321").render("", "מוסד", "כותרת", "")

    assert "h1{color:#123456;font-size:20pt}" in html
    assert "color:#654321" in html


def test_document_css_is_appended_after_the_base() -> None:
    html = _shell().render("h2{color:red}", "מוסד", "כותרת", "")

    assert html.index("h1{color:") < html.index("h2{color:red}")
