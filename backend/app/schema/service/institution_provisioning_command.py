from pydantic import BaseModel, EmailStr


class InstitutionProvisioningCommand(BaseModel):
    name: str
    manager_full_name: str
    manager_email: EmailStr
    contact_name: str | None = None
    contact_phone: str | None = None
