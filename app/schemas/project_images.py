from pydantic import BaseModel, ConfigDict, field_serializer

from app.core.config import settings


class ProjectImageCreate(BaseModel):
    project_id: int
    title: str
    description: str | None = None
    image_url: str
    display_order: int


class ProjectImageUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    display_order: int | None = None

class ProjectImageResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None = None
    image_url: str
    display_order: int

    @field_serializer("image_url")
    def serialize_image_url(self, image_url: str) -> str:
        return settings.asset_url(image_url)

    model_config = ConfigDict(from_attributes=True)
