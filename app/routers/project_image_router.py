from fastapi import APIRouter, Depends

from app.dependencies.project_image_dependencies import get_project_image_service
from app.dependencies.auth_dependencies import get_current_user

from app.schemas.project_images import (
    ProjectImageCreate,
    ProjectImageResponse,
    ProjectImageUpdate,
)

from app.services.project_image_service import ProjectImageService


router = APIRouter(
    prefix="/project-images",
    tags=["project-images"]
)


@router.post(
    "/",
    response_model=ProjectImageResponse,
    status_code=201
)
def create_project_image(
    project_image_create: ProjectImageCreate,
    service: ProjectImageService = Depends(get_project_image_service),
    current_user: str = Depends(get_current_user),
):
    return service.create(project_image_create)


@router.get(
    "/{project_image_id}",
    response_model=ProjectImageResponse
)
def get_project_image(
    project_image_id: int,
    service: ProjectImageService = Depends(get_project_image_service),
):
    project_image = service.get_by_id(project_image_id)
    return project_image


@router.delete(
    "/{project_image_id}",
    status_code=204
)
def delete_project_image(
    project_image_id: int,
    service: ProjectImageService = Depends(get_project_image_service),
    current_user: str = Depends(get_current_user),
):
    project_image = service.get_by_id(project_image_id)
    service.delete(project_image)


@router.put(
    "/{project_image_id}",
    response_model=ProjectImageResponse
)
def update_project_image(
    project_image_id: int,
    project_image_update: ProjectImageUpdate,
    service: ProjectImageService = Depends(get_project_image_service),
    current_user: str = Depends(get_current_user),
):
    project_image = service.get_by_id(project_image_id)
    return service.update(project_image, project_image_update)