from pydantic import BaseModel, ConfigDict


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


    model_config = ConfigDict(from_attributes=True)