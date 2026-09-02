from dataclasses import dataclass

from backend.app.models.client.user_role import UserRole

DEMO_PASSWORD = "demo1234"
DEMO_INSTITUTION_NAME = "מוסד הדגמה"
DEMO_INSTITUTION_CODE = "demo"


@dataclass(frozen=True)
class DemoAccount:
    username: str
    full_name: str
    email: str
    role: UserRole


MANAGER = DemoAccount("mor", "מור מנהלת", "mor@demo.aleisiach.org", UserRole.MANAGER)
INSTRUCTOR = DemoAccount("dana", "דנה מדריכה", "dana@demo.aleisiach.org", UserRole.INSTRUCTOR)
PROFESSIONAL_TEACHER = DemoAccount(
    "yoav", "יואב מורה מקצועי", "yoav@demo.aleisiach.org", UserRole.PROFESSIONAL_TEACHER
)

ALL_ACCOUNTS: tuple[DemoAccount, ...] = (MANAGER, INSTRUCTOR, PROFESSIONAL_TEACHER)
