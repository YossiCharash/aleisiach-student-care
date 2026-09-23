from datetime import date
from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.schema.service.document_meta import DocumentMeta
from backend.app.utils.service.brand_logo import BrandLogo


class DocumentShell:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand
        self._logo = BrandLogo.data_uri(brand.logo_path)

    def field(self, label: str, value: str | None) -> str:
        shown = escape(value) if value else "—"
        return f'<div class="field"><span class="label">{escape(label)}: </span>{shown}</div>'

    def value(self, value: object) -> str:
        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")
        text = str(value) if value else ""
        return escape(text) if text else "—"

    def base_css(self, meta: DocumentMeta) -> str:
        return (
            "@page{size:A4;margin:1.6cm 1.6cm 1.9cm 1.6cm;"
            f'@bottom-right{{content:"{self._css_str(meta.institution_name)}";'
            f"font-family:{self._brand.font_family};font-size:8pt;color:{self._brand.muted_color}}}"
            f'@bottom-left{{content:"{self._footer_left(meta)}";'
            f"font-family:{self._brand.font_family};font-size:8pt;color:{self._brand.muted_color}}}"
            '@bottom-center{content:"עמוד " counter(page) " מתוך " counter(pages);'
            f"font-family:{self._brand.font_family};font-size:8pt;"
            f"color:{self._brand.muted_color}}}}}"
            f"body{{font-family:{self._brand.font_family};direction:rtl;"
            f"color:{self._brand.text_color};margin:0;font-size:11pt}}"
            ".doc-header{display:flex;align-items:center;justify-content:space-between;"
            f"background:{self._brand.primary_color};padding:0.45cm 0.55cm;"
            "border-radius:8pt 8pt 0 0}"
            ".doc-title{color:#ffffff;font-size:18pt;font-weight:700;margin:0}"
            ".doc-institution{color:#d9ecc7;font-size:10pt;margin:3pt 0 0}"
            ".doc-logo{background:#ffffff;border-radius:6pt;padding:4pt 7pt}"
            ".doc-logo img{display:block;height:1.4cm;width:auto}"
            f".doc-stripe{{height:5pt;background:{self._brand.accent_color};"
            "border-radius:0 0 3pt 3pt}"
            ".doc-meta{margin-top:0.5cm;background:#f4f7ee;border:0.5pt solid #dce9c9;"
            "border-radius:8pt;padding:0.28cm 0.4cm;display:flex;flex-wrap:wrap}"
            ".doc-meta-item{width:50%;font-size:10.5pt;margin:3pt 0}"
            f".doc-meta-label{{color:{self._brand.muted_color}}}"
            f".doc-meta-value{{color:{self._brand.primary_color};font-weight:700}}"
            ".doc-content{margin-top:0.55cm}"
        )

    def render(self, css: str, meta: DocumentMeta, body: str) -> str:
        return (
            '<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">'
            f"<style>{self.base_css(meta)}{css}</style></head><body>"
            f"{self._header(meta)}{self._meta_card(meta)}"
            f'<div class="doc-content">{body}</div></body></html>'
        )

    def _header(self, meta: DocumentMeta) -> str:
        institution = escape(meta.institution_name)
        tagline = escape(self._brand.institution_tagline)
        subtitle = f"{institution} — {tagline}" if tagline else institution
        return (
            '<div class="doc-header">'
            f'<div><p class="doc-title">{escape(meta.title)}</p>'
            f'<p class="doc-institution">{subtitle}</p></div>'
            f"{self._logo_block()}</div>"
            '<div class="doc-stripe"></div>'
        )

    def _logo_block(self) -> str:
        if not self._logo:
            return ""
        return f'<div class="doc-logo"><img src="{self._logo}" alt=""></div>'

    def _meta_card(self, meta: DocumentMeta) -> str:
        items = [self._meta_item("שם התלמיד", escape(meta.student_name), strong=True)]
        if meta.content_date is not None:
            items.append(self._meta_item("תאריך", self.value(meta.content_date)))
        items.append(self._meta_item("תאריך הנפקה", self.value(meta.issue_date)))
        items.append(self._meta_item("הופק על ידי", escape(meta.issued_by)))
        return f'<div class="doc-meta">{"".join(items)}</div>'

    def _meta_item(self, label: str, value: str, strong: bool = False) -> str:
        css_class = "doc-meta-value" if strong else ""
        value_html = f'<span class="{css_class}">{value}</span>' if css_class else value
        return (
            '<div class="doc-meta-item">'
            f'<span class="doc-meta-label">{escape(label)}: </span>{value_html}</div>'
        )

    def _footer_left(self, meta: DocumentMeta) -> str:
        issued_by = self._css_str(meta.issued_by)
        return f"הופק על ידי {issued_by} · {meta.issue_date.strftime('%d/%m/%Y')}"

    def _css_str(self, text: str) -> str:
        cleaned = text.replace("<", "").replace(">", "")
        return cleaned.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
