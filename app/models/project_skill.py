from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.database.database import Base


class ProjectSkill(Base):
    __tablename__ = "project_skills"
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        primary_key=True)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"),
        primary_key=True)