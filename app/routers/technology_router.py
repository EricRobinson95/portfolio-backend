from fastapi import APIRouter, Depends

from app.dependencies.technology_dependencies import get_technology_service
from app.dependencies.auth_dependencies import get_current_user

from app.schemas.technology import (
    TechnologyCreate,
    TechnologyResponse,
    TechnologyUpdate,
)

from app.services.technology_service import TechnologyService


router = APIRouter(
    prefix="/technologies",
    tags=["technologies"]
)


@router.post(
    "/",
    response_model=TechnologyResponse,
    status_code=201
)
def create_technology(
    technology_create: TechnologyCreate,
    service: TechnologyService = Depends(get_technology_service),
    current_user: str = Depends(get_current_user),
):
    return service.create(technology_create)


@router.get(
    "/",
    response_model=list[TechnologyResponse]
)
def get_all_technologies(
    service: TechnologyService = Depends(get_technology_service),
):
    return service.get_all()


@router.get(
    "/{technology_id}",
    response_model=TechnologyResponse
)
def get_technology(
    technology_id: int,
    service: TechnologyService = Depends(get_technology_service),
):
    technology = service.get_by_id(technology_id)
    return technology


@router.delete(
    "/{technology_id}",
    status_code=204
)
def delete_technology(
    technology_id: int,
    service: TechnologyService = Depends(get_technology_service),
    current_user: str = Depends(get_current_user),
):
    technology = service.get_by_id(technology_id)
    service.delete(technology)


@router.put(
    "/{technology_id}",
    response_model=TechnologyResponse
)
def update_technology(
    technology_id: int,
    technology_update: TechnologyUpdate,
    service: TechnologyService = Depends(get_technology_service),
    current_user: str = Depends(get_current_user),
):
    technology = service.get_by_id(technology_id)
    return service.update(technology, technology_update)