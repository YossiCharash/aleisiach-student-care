from backend.app.configuration.pdf.brand_settings import BrandSettings
from backend.app.utils.service.brand_logo import BrandLogo


def test_data_uri_encodes_the_bundled_logo() -> None:
    uri = BrandLogo.data_uri(BrandSettings().logo_path)

    assert uri.startswith("data:image/png;base64,")
    assert len(uri) > len("data:image/png;base64,")


def test_missing_file_yields_an_empty_string() -> None:
    assert BrandLogo.data_uri("nonexistent-logo-file.png") == ""
