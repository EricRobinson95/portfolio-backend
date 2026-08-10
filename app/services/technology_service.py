from app.models.technology import Technology
from app.repositories.technology_repository import TechnologyRepository
from app.schemas.technology import TechnologyCreate, TechnologyUpdate
from app.exceptions.technology_exception import DuplicateTechnologyNameError, TechnologyNotFoundError



class TechnologyService:
    def __init__(self, repository:TechnologyRepository):
        self.repository = repository

    def create(self, technology_create: TechnologyCreate) -> Technology:
        existing_technology = self.repository.get_by_name(
            technology_create.name
        )
        if existing_technology is not None:
            raise DuplicateTechnologyNameError(technology_create.name)
        technology = Technology(
            name=technology_create.name,
            icon=technology_create.icon,
            description=technology_create.description,
        )
        return self.repository.create(technology)

    def get_all(self) -> list[Technology]:
        return self.repository.get_all()

    def get_by_id(self, technology_id: int) -> Technology:
        technology = self.repository.get_by_id(technology_id)
        if technology is None:
            raise TechnologyNotFoundError(technology_id)
        return technology


    def update(self, technology:Technology, technology_update: TechnologyUpdate) -> Technology:
        if technology_update.name is not None:
            existing_name = self.repository.get_by_name(technology_update.name)
            if existing_name is not None and existing_name.id != technology.id:
                raise DuplicateTechnologyNameError(technology_update.name)
            technology.name = technology_update.name
        if technology_update.icon is not None:
            technology.icon = technology_update.icon
        if technology_update.description is not None:
            technology.description = technology_update.description
        return self.repository.update(technology)

    def delete(self, technology:Technology) -> None:
        self.repository.delete(technology)