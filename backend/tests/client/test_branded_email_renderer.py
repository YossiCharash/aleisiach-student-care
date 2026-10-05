from backend.app.client.email.branded_email_renderer import BrandedEmailRenderer
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.schema.service.password_reset_message import PasswordResetMessage


def _renderer() -> BrandedEmailRenderer:
    settings = EmailSettings(invite_base_url="https://app.example.com/accept-invitation")
    return BrandedEmailRenderer(settings)


def test_invitation_is_branded_html_with_no_reply_notice() -> None:
    rendered = _renderer().invitation("https://app.example.com/accept?token=abc123")

    assert rendered.subject == "הזמנה למערכת עלי שיח"
    assert "abc123" in rendered.html_body
    assert "abc123" in rendered.text_body
    assert "השלמת הרשמה" in rendered.html_body
    assert "נא לא להשיב" in rendered.html_body
    assert "נא לא להשיב" in rendered.text_body
    assert "https://app.example.com/logo.png" in rendered.html_body


def test_reset_includes_account_details() -> None:
    message = PasswordResetMessage(
        email="user@example.com",
        link="https://app.example.com/reset?token=xyz789",
        institution_name="מוסד בדיקה",
        username="tester",
    )

    rendered = _renderer().password_reset(message)

    assert rendered.subject == "איפוס סיסמה — עלי שיח"
    assert "tester · מוסד בדיקה" in rendered.html_body
    assert "xyz789" in rendered.text_body


def test_logo_url_prefers_explicit_override() -> None:
    renderer = BrandedEmailRenderer(
        EmailSettings(brand_logo_url="https://cdn.example.com/brand.png")
    )

    rendered = renderer.invitation("https://app.example.com/accept?token=abc")

    assert "https://cdn.example.com/brand.png" in rendered.html_body
