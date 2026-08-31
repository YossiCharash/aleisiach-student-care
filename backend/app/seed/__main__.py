from collections.abc import Iterator

from sqlalchemy.orm import Session

from backend.app.client.database.database import Database
from backend.app.configuration.settings import Settings
from backend.app.seed.demo_credentials import ALL_ACCOUNTS, DEMO_PASSWORD
from backend.app.seed.demo_seeder import DemoSeeder
from backend.app.utils.service.password_hasher import PasswordHasher


def main() -> None:
    settings = Settings()
    if settings.app.environment == "production":
        raise SystemExit("סירוב לזרוע נתוני דמו בסביבת פרודקשן.")
    database = Database(settings.database)
    generator = database.session()
    session = next(generator)
    was_seeded = DemoSeeder(session, PasswordHasher()).is_seeded()
    _seed(session, generator)
    _print_summary(was_seeded)


def _seed(session: Session, generator: Iterator[Session]) -> None:
    try:
        DemoSeeder(session, PasswordHasher()).run()
    except BaseException:
        session.rollback()
        raise
    finally:
        next(generator, None)


def _print_summary(was_seeded: bool) -> None:
    if was_seeded:
        print("נתוני הדמו כבר קיימים — לא בוצע שינוי.")
        return
    print("נתוני דמו נזרעו בהצלחה. פרטי כניסה (סיסמה זהה לכולם):")
    print(f"  סיסמה: {DEMO_PASSWORD}")
    for account in ALL_ACCOUNTS:
        print(f"  {account.role.value:22} username={account.username}")


if __name__ == "__main__":
    main()
