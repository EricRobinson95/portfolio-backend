from pydantic import BaseModel, ConfigDict


class TechnologyCreate(BaseModel):
    name: str
    icon: str | None = None
    description: str | None = None


class TechnologyUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    description: str | None = None

class TechnologyResponse(BaseModel):
    id: int
    name: str
    icon: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)