from pydantic import BaseModel, EmailStr


class InstitutionProvisioningCommand(BaseModel):
    name: str
    code: str
    manager_full_name: str
    manager_email: EmailStr
