

from pydantic import BaseModel, ConfigDict, field_serializer

from app.core.config import settings
from app.schemas.technology import TechnologyResponse
from app.schemas.skill import SkillResponse


class ProjectCreate(BaseModel):
    title: str
    github_url: str
    image_thumbnail_url: str
    description: str


class ProjectUpdate(BaseModel):
    title: str | None = None
    github_url: str | None = None
    image_thumbnail_url: str  | None = None
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    github_url: str
    image_thumbnail_url: str
    description:str
    technologies: list["TechnologyResponse"] | None = None
    skills: list["SkillResponse"] | None = None

    @field_serializer("image_thumbnail_url")
    def serialize_thumbnail_url(self, image_thumbnail_url: str) -> str:
        return settings.asset_url(image_thumbnail_url)

    model_config = ConfigDict(from_attributes=True)
