from app.exceptions.project_technology_exceptions import ProjectTechnologyAlreadyExistsError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.technology_repository import TechnologyRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.exceptions.project_exceptions import DuplicateProjectTitleError ,ProjectNotFoundError
from app.exceptions.technology_exception import TechnologyNotFoundError
from app.exceptions.project_technology_exceptions import ProjectTechnologyNotFoundError
from app.repositories.project_technology_repository import ProjectTechnologyRepository
from app.repositories.project_skill_repository import ProjectSkillRepository
from app.exceptions.project_skill_exceptions import ProjectSkillAlreadyExistsError, ProjectSkillNotFoundError
from app.exceptions.skill_exceptions import SkillNotFoundError
from app.repositories.skill_repository import SkillRepository

class ProjectService:
    def __init__(self,
                project_repository:ProjectRepository,
                technology_repository:TechnologyRepository,
                project_technology_repository:ProjectTechnologyRepository,
                skill_repository: SkillRepository,
                project_skill_repository: ProjectSkillRepository
                ):
        self.project_repository = project_repository
        self.technology_repository = technology_repository
        self.project_technology_repository = project_technology_repository
        self.skill_repository = skill_repository
        self.project_skill_repository = project_skill_repository

    def create(self, project_create: ProjectCreate) -> Project:
        existing_project = self.project_repository.get_by_title(
            project_create.title
            )
        if existing_project is not None:
            raise  DuplicateProjectTitleError(project_create.title)
        project = Project(
            title=project_create.title,
            github_url=project_create.github_url,
            image_thumbnail_url=project_create.image_thumbnail_url,
            description=project_create.description,
        )
        return self.project_repository.create(project)

    def get_all(self) -> list[Project]:
        return self.project_repository.get_all()

    def get_by_id(self, project_id: int) -> Project:
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return project

    def update(self, project:Project, project_update: ProjectUpdate) -> Project:
        if project_update.title is not None:
            existing_title = self.project_repository.get_by_title(project_update.title)
            if existing_title is not None and existing_title.id != project.id:
                raise DuplicateProjectTitleError(project_update.title)
            project.title = project_update.title
        if project_update.github_url is not None:
            project.github_url = project_update.github_url
        if project_update.image_thumbnail_url is not None:
            project.image_thumbnail_url = project_update.image_thumbnail_url
        if project_update.description is not None:
            project.description = project_update.description
        return self.project_repository.update(project)

    def delete(self, project:Project) -> None:
        self.project_repository.delete(project)

    def get_technologies(self, project_id: int):
        project = self.get_by_id(project_id)
        return project.technologies

    def add_technology(self, project_id: int, technology_id: int) -> None:
        self.get_by_id(project_id)
        technology = self.technology_repository.get_by_id(technology_id)
        if not technology:
            raise TechnologyNotFoundError(technology_id)
        if self.project_technology_repository.exists(project_id, technology_id):
            raise ProjectTechnologyAlreadyExistsError(project_id, technology_id)
        self.project_technology_repository.create(project_id, technology_id)

    def delete_technology(self, project_id: int, technology_id: int) -> None:
        self.get_by_id(project_id)
        technology = self.technology_repository.get_by_id(technology_id)
        if not technology:
            raise TechnologyNotFoundError(technology_id)
        if not self.project_technology_repository.exists(project_id, technology_id):
            raise ProjectTechnologyNotFoundError(project_id, technology_id)
        self.project_technology_repository.delete(project_id, technology_id)

    def get_skills(self, project_id: int):
        project = self.get_by_id(project_id)
        return project.skills

    def add_skill(self, project_id: int, skill_id: int) -> None:
        self.get_by_id(project_id)
        skill = self.skill_repository.get_by_id(skill_id)
        if not skill:
            raise SkillNotFoundError(skill_id)
        if self.project_skill_repository.exists(project_id, skill_id):
            raise ProjectSkillAlreadyExistsError(project_id, skill_id)
        self.project_skill_repository.create(project_id, skill_id)

    def delete_skill(self, project_id: int, skill_id: int) -> None:
        self.get_by_id(project_id)
        skill = self.skill_repository.get_by_id(skill_id)
        if not skill:
            raise SkillNotFoundError(skill_id)
        if not self.project_skill_repository.exists(project_id, skill_id):
            raise ProjectSkillNotFoundError(project_id, skill_id)
        self.project_skill_repository.delete(project_id, skill_id)