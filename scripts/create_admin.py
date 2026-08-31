from app.core.config import settings
from app.core.security import hash_password
from app.database.database import SessionLocal
from app.models.admin import Admin


def create_admin() -> None:
    db = SessionLocal()

    try:
        existing_admin = (
            db.query(Admin)
            .filter(Admin.username == settings.admin_username)
            .first()
        )

        if existing_admin:
            print("Admin already exists.")
            return

        admin = Admin(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()