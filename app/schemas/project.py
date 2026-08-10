

from pydantic import BaseModel, ConfigDict

from app.schemas.technology import TechnologyResponse


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

    model_config = ConfigDict(from_attributes=True)