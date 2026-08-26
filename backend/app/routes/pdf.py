from typing import Annotated

from fastapi import Depends

from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap


def get_pdf_renderer(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> PdfRenderer:
    return bootstrap.pdf_renderer


RendererDep = Annotated[PdfRenderer, Depends(get_pdf_renderer)]
