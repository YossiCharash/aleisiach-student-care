from html import escape

from backend.app.configuration.pdf.brand_settings import BrandSettings


class DocumentShell:
    def __init__(self, brand: BrandSettings) -> None:
        self._brand = brand

    def base_css(self) -> str:
        return (
            f"body{{font-family:{self._brand.font_family};direction:rtl;"
            f"color:{self._brand.text_color};margin:2cm}}"
            f"h1{{color:{self._brand.primary_color};font-size:20pt}}"
            f".institution{{color:{self._brand.muted_color};font-size:11pt;margin:0}}"
        )

    def render(self, css: str, institution_name: str, title: str, body: str) -> str:
        return (
            '<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">'
            f"<style>{self.base_css()}{css}</style></head><body>"
            f'<p class="institution">{escape(institution_name)}</p>'
            f"<h1>{title}</h1>{body}</body></html>"
        )
