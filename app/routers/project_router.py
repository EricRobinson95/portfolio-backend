from fastapi import APIRouter, Depends
from app.dependencies.project_dependencies import get_project_service
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService
from app.dependencies.project_image_dependencies import get_project_image_service
from app.schemas.project_images import ProjectImageResponse
from app.schemas.technology import TechnologyResponse
from app.schemas.skill import SkillResponse
from app.services.project_image_service import ProjectImageService

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


@router.post("/",
            response_model=ProjectResponse,
            status_code=201)
def create_project(
    project_create: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    ):
    return service.create(project_create)


@router.get("/",
            response_model=list[ProjectResponse])
def get_all_projects(
    service: ProjectService = Depends(get_project_service),
    ):
    return service.get_all()


@router.get("/{project_id}",
            response_model=ProjectResponse)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    ):
    project = service.get_by_id(project_id)
    return project


@router.delete("/{project_id}",
            status_code=204)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    ):
    project = service.get_by_id(project_id)
    service.delete(project)


@router.put("/{project_id}",
            response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
    ):
    project = service.get_by_id(project_id)
    return service.update(project, project_update)

@router.post("/{project_id}/technologies/{technology_id}",
            status_code=204)
def add_technology(
    project_id: int,
    technology_id: int,
    service: ProjectService = Depends(get_project_service),
    ):
    service.add_technology(project_id, technology_id)
    return None

@router.get("/{project_id}/technologies",
            response_model=list[TechnologyResponse])
def get_project_technologies(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    return service.get_technologies(project_id)

@router.delete("/{project_id}/technologies/{technology_id}",
            status_code=204)
def delete_technology(
    project_id: int,
    technology_id: int,
    service: ProjectService = Depends(get_project_service),
    ):
    service.delete_technology(project_id, technology_id)
    return None

@router.post("/{project_id}/skills/{skill_id}",
            status_code=204)
def add_skill(
    project_id: int,
    skill_id: int,
    service: ProjectService = Depends(get_project_service),
    ):
    service.add_skill(project_id, skill_id)
    return None

@router.get("/{project_id}/skills",
            response_model=list[SkillResponse])
def get_project_skills(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    return service.get_skills(project_id)

@router.delete("/{project_id}/skills/{skill_id}",
            status_code=204)
def delete_skill(
    project_id: int,
    skill_id: int,
    service: ProjectService = Depends(get_project_service),
    ):
    service.delete_skill(project_id, skill_id)
    return None

@router.get("/{project_id}/images",
            response_model=list[ProjectImageResponse])
def get_project_images(
    project_id: int,
    service: ProjectImageService = Depends(get_project_image_service),
    ):
    return service.get_by_project_id(project_id)
