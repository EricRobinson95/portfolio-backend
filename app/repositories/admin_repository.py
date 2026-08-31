from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin import Admin


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Admin | None:
        statement = select(Admin).where(
            Admin.username == username
        )

        result = self.db.execute(statement)

        return result.scalars().one_or_none()