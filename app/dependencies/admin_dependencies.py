from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.admin_repository import AdminRepository


def get_admin_repository(
    db: Session = Depends(get_db),
) -> AdminRepository:
    return AdminRepository(db)