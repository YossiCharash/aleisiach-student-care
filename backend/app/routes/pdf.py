from typing import Annotated

from fastapi import Depends

from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.configuration.provider import get_bootstrap


def get_pdf_renderer(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> PdfRenderer:
    return bootstrap.pdf_renderer


RendererDep = Annotated[PdfRenderer, Depends(get_pdf_renderer)]


def get_brand_settings(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> BrandSettings:
    return bootstrap.settings.brand


BrandDep = Annotated[BrandSettings, Depends(get_brand_settings)]
