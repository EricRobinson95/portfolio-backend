from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.database.database import Base


class ProjectTechnology(Base):
    __tablename__ = "project_technologies"
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        primary_key=True)
    technology_id: Mapped[int] = mapped_column(
        ForeignKey("technologies.id"),
        primary_key=True)



