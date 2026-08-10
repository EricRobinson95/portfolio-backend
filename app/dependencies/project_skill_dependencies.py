from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.project_skill_repository import ProjectSkillRepository

def get_project_skill_repository(
        db: Session = Depends(get_db)
        ) -> ProjectSkillRepository:
    return ProjectSkillRepository(db)
