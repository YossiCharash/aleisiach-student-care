from pydantic import BaseModel


class RenderedEmail(BaseModel):
    subject: str
    text_body: str
    html_body: str
