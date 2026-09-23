from datetime import date

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.utils.service.document_shell import DocumentShell


def _shell(**overrides: str) -> DocumentShell:
    return DocumentShell(BrandSettings(_env_file=None, **overrides))


def _meta(**overrides: object) -> DocumentMeta:
    base: dict[str, object] = {
        "title": "פרטי תלמיד",
        "institution_name": "מוסד בדיקה",
        "student_name": "נועה",
        "issued_by": "רונית",
        "issue_date": date(2026, 9, 23),
    }
    base.update(overrides)
    return DocumentMeta(**base)


def test_shell_wraps_the_body_in_an_rtl_hebrew_page() -> None:
    html = _shell().render("", _meta(), "<p>גוף</p>")

    assert html.startswith("<!doctype html>")
    assert 'dir="rtl"' in html
    assert 'lang="he"' in html
    assert "פרטי תלמיד" in html
    assert "<p>גוף</p>" in html


def test_meta_card_shows_student_issue_date_and_issuer() -> None:
    html = _shell().render("", _meta(), "")

    assert "שם התלמיד" in html
    assert "נועה" in html
    assert "תאריך הנפקה" in html
    assert "23/09/2026" in html
    assert "הופק על ידי" in html
    assert "רונית" in html


def test_content_date_is_shown_only_when_present() -> None:
    without = _shell().render("", _meta(), "")
    with_date = _shell().render("", _meta(content_date=date(2026, 9, 12)), "")

    assert ">תאריך: " not in without.replace("תאריך הנפקה", "")
    assert "12/09/2026" in with_date


def test_shell_escapes_the_institution_name_in_the_header() -> None:
    html = _shell().render("", _meta(institution_name="<script>x</script>"), "")

    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_base_css_follows_the_configured_brand() -> None:
    html = _shell(primary_color="#123456", text_color="#654321").render("", _meta(), "")

    assert "#123456" in html
    assert "color:#654321" in html


def test_document_css_is_appended_after_the_base() -> None:
    html = _shell().render("h2{color:red}", _meta(), "")

    assert html.index(".doc-header{") < html.index("h2{color:red}")


def test_the_footer_carries_the_issuer_and_issue_date() -> None:
    html = _shell().render("", _meta(issued_by="רונית", issue_date=date(2026, 9, 23)), "")

    assert "הופק על ידי רונית · 23/09/2026" in html
