from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.technology_repository import TechnologyRepository
from app.services.technology_service import TechnologyService

def get_technology_repository(
        db: Session = Depends(get_db)
        ) -> TechnologyRepository:
    return TechnologyRepository(db)

def get_technology_service(
        repository: TechnologyRepository = Depends(get_technology_repository)
        ) -> TechnologyService:
    return TechnologyService(repository)