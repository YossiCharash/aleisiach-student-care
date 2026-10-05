from html import escape
from pathlib import Path
from string import Template

from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.schema.client.email.rendered_email import RenderedEmail
from backend.app.schema.service.password_reset_message import PasswordResetMessage

_INVITE_SUBJECT = "הזמנה למערכת עלי שיח"
_RESET_SUBJECT = "איפוס סיסמה — עלי שיח"
_NO_REPLY = "הודעה זו נשלחה באופן אוטומטי — נא לא להשיב להודעה זו."
_IGNORE = "אם ההודעה הגיעה אליך בטעות, ניתן להתעלם ממנה."
_TEMPLATE = Template(
    (Path(__file__).parent / "templates" / "branded_email.html").read_text(encoding="utf-8")
)


class BrandedEmailRenderer:
    def __init__(self, settings: EmailSettings) -> None:
        self._settings = settings

    def invitation(self, link: str) -> RenderedEmail:
        heading = f"הוזמנת למערכת {self._settings.app_name}"
        lead = (
            "נוצר עבורך חשבון במערכת לניהול תיק מקבל שרות. "
            "להשלמת ההרשמה ובחירת שם משתמש וסיסמה, לחצו על הכפתור:"
        )
        html = self._document(heading, lead, "השלמת הרשמה", link)
        text = self._text(heading, lead, "להשלמת ההרשמה", link)
        return RenderedEmail(subject=_INVITE_SUBJECT, text_body=text, html_body=html)

    def password_reset(self, message: PasswordResetMessage) -> RenderedEmail:
        heading = "בקשת איפוס סיסמה"
        account = f"{message.username} · {message.institution_name}"
        lead = (
            f"התקבלה בקשה לאיפוס סיסמה עבור החשבון {account}. " "לבחירת סיסמה חדשה, לחצו על הכפתור:"
        )
        html = self._document(heading, lead, "איפוס סיסמה", message.link)
        text = self._text(heading, lead, "לאיפוס הסיסמה", message.link)
        return RenderedEmail(subject=_RESET_SUBJECT, text_body=text, html_body=html)

    def _document(self, heading: str, lead: str, button_label: str, link: str) -> str:
        return _TEMPLATE.substitute(
            app_name=escape(self._settings.app_name),
            logo_url=escape(self._settings.logo_url),
            heading=escape(heading),
            lead=escape(lead),
            button_label=escape(button_label),
            link=escape(link),
            no_reply=escape(_NO_REPLY),
            ignore=escape(_IGNORE),
        )

    def _text(self, heading: str, lead: str, action_label: str, link: str) -> str:
        return (
            f"{heading}\n\n{lead}\n\n{action_label}:\n{link}\n\n"
            f"{_NO_REPLY}\n{_IGNORE}\n\n{self._settings.app_name} · ליווי וקידום אישי"
        )
