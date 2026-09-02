from pydantic import BaseModel, EmailStr


class InstitutionProvisioningCommand(BaseModel):
    name: str
    code: str
    manager_full_name: str
    manager_email: EmailStr
    contact_name: str | None = None
    contact_phone: str | None = None
