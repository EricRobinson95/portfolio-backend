from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.project_technology_repository import ProjectTechnologyRepository

def get_project_technology_repository(
        db: Session = Depends(get_db)
        ) -> ProjectTechnologyRepository:
    return ProjectTechnologyRepository(db)
