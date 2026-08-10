from fastapi import APIRouter, Depends
from app.dependencies.skill_dependencies import get_skill_service
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.services.skill_service import SkillService

router = APIRouter(
    prefix="/skills",
    tags=["skills"]
)


@router.post("/",
            response_model=SkillResponse,
            status_code=201)
def create_skill(
    skill_create: SkillCreate,
    service: SkillService = Depends(get_skill_service),
    ):
    return service.create(skill_create)


@router.get("/",
            response_model=list[SkillResponse])
def get_all_skills(
    service: SkillService = Depends(get_skill_service),
    ):
    return service.get_all()


@router.get("/{skill_id}",
            response_model=SkillResponse)
def get_skill(
    skill_id: int,
    service: SkillService = Depends(get_skill_service),
    ):
    skill = service.get_by_id(skill_id)
    return skill


@router.delete("/{skill_id}",
            status_code=204)
def delete_skill(
    skill_id: int,
    service: SkillService = Depends(get_skill_service),
    ):
    skill = service.get_by_id(skill_id)
    service.delete(skill)


@router.put("/{skill_id}",
            response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    service: SkillService = Depends(get_skill_service),
    ):
    skill = service.get_by_id(skill_id)
    return service.update(skill, skill_update)


