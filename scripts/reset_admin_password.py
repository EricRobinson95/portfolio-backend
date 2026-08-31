from app.core.config import settings
from app.core.security import hash_password
from app.database.database import SessionLocal
from app.models.admin import Admin


def reset_admin_password() -> None:
    db = SessionLocal()

    try:
        admin = (
            db.query(Admin)
            .filter(Admin.username == settings.admin_username)
            .first()
        )

        if admin is None:
            print("Admin not found.")
            return

        admin.password_hash = hash_password(
            settings.admin_password
        )

        db.commit()

        print("Admin password reset successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    reset_admin_password()