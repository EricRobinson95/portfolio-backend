from app.core.config import settings
from app.core.security import hash_password
from app.database.database import SessionLocal
from app.models.admin import Admin
from app.core.security_logging import configure_security_logging, log_security_event
from uuid import uuid4


def reset_admin_password() -> None:
    configure_security_logging()
    operation_id = str(uuid4())

    def record(outcome, reason=None):
        log_security_event(
            action="admin_password_reset", outcome=outcome,
            source="operator_script", operation_id=operation_id, reason=reason,
        )

    record("started")
    db = None

    try:
        db = SessionLocal()
        admin = (
            db.query(Admin)
            .filter(Admin.username == settings.admin_username)
            .first()
        )

        if admin is None:
            record("rejected", "account_not_found")
            print("Admin not found.")
            return

        admin.password_hash = hash_password(
            settings.admin_password
        )

        db.commit()
        record("success")

        print("Admin password reset successfully.")

    except Exception:
        record("error", "reset_failed")
        if db is not None:
            db.rollback()
        raise
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    reset_admin_password()
