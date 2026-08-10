from app.models.skill import Skill
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate
from app.exceptions.skill_exceptions import SkillNotFoundError, DuplicateSkillNameError



class SkillService:
    def __init__(self, repository:SkillRepository):
        self.repository = repository

    def create(self, skill_create: SkillCreate) -> Skill:
        existing_skill = self.repository.get_by_name(
            skill_create.name
        )
        if existing_skill is not None:
            raise DuplicateSkillNameError(skill_create.name)
        skill = Skill(
            name=skill_create.name,
            description=skill_create.description,
        )
        return self.repository.create(skill)

    def get_all(self) -> list[Skill]:
        return self.repository.get_all()

    def get_by_id(self, skill_id: int) -> Skill:
        skill = self.repository.get_by_id(skill_id)
        if skill is None:
            raise SkillNotFoundError(skill_id)
        return skill


    def update(self, skill:Skill, skill_update: SkillUpdate) -> Skill:
        if skill_update.name is not None:
            existing_name = self.repository.get_by_name(skill_update.name)
            if existing_name is not None and existing_name.id != skill.id:
                raise DuplicateSkillNameError(skill_update.name)
            skill.name = skill_update.name
        if skill_update.description is not None:
            skill.description = skill_update.description
        return self.repository.update(skill)

    def delete(self, skill:Skill) -> None:
        self.repository.delete(skill)