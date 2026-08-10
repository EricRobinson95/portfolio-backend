from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.project_image_repository import ProjectImageRepository
from app.repositories.project_repository import ProjectRepository
from app.services.project_image_service import ProjectImageService
from app.dependencies.project_dependencies import get_project_repository

def get_project_image_repository(
        db: Session = Depends(get_db)
        ) -> ProjectImageRepository:
    return ProjectImageRepository(db)

def get_project_image_service(
        project_image_repository: ProjectImageRepository = Depends(get_project_image_repository),
        project_repository: ProjectRepository = Depends(get_project_repository)

        ) -> ProjectImageService:
    return ProjectImageService(project_image_repository,
                            project_repository)