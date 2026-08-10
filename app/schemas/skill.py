from pydantic import BaseModel, ConfigDict


class SkillCreate(BaseModel):
    name: str
    description: str | None = None


class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class SkillResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)