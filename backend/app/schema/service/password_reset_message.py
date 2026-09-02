from pydantic import BaseModel


class PasswordResetMessage(BaseModel):
    email: str
    link: str
    institution_name: str
    username: str
