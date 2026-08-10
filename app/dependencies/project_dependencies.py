from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.dependencies.project_technology_dependencies import get_project_technology_repository
from app.dependencies.technology_dependencies import get_technology_repository
from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService
from app.repositories.technology_repository import TechnologyRepository
from app.repositories.project_technology_repository import ProjectTechnologyRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.project_skill_repository import ProjectSkillRepository
from app.dependencies.skill_dependencies import get_skill_repository
from app.dependencies.project_skill_dependencies import get_project_skill_repository
def get_project_repository(
        db: Session = Depends(get_db)
        ) -> ProjectRepository:
    return ProjectRepository(db)

def get_project_service(
        project_repository: ProjectRepository = Depends(
            get_project_repository),
        technology_repository: TechnologyRepository = Depends(
            get_technology_repository),
        project_technology_repository: ProjectTechnologyRepository = Depends(
            get_project_technology_repository),
        skill_repository: SkillRepository = Depends(
            get_skill_repository),
            project_skill_repository: ProjectSkillRepository = Depends(
                get_project_skill_repository
            )
        ) -> ProjectService:
    return ProjectService(project_repository,
                        technology_repository,
                        project_technology_repository,
                        skill_repository,
                        project_skill_repository)