from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.skill_repository import SkillRepository
from app.services.skill_service import SkillService

def get_skill_repository(
        db: Session = Depends(get_db)
        ) -> SkillRepository:
    return SkillRepository(db)

def get_skill_service(
        repository: SkillRepository = Depends(get_skill_repository)
        ) -> SkillService:
    return SkillService(repository)