from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
if TYPE_CHECKING:
    from app.models.technology import Technology
    from app.models.skill import Skill
    from app.models.project_image import ProjectImage



class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100),
                                    unique=True)
    github_url: Mapped[str] = mapped_column(String(200))
    image_thumbnail_url: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    technologies: Mapped[list["Technology"]] = relationship(
        secondary="project_technologies", back_populates="projects")
    skills: Mapped[list["Skill"]] = relationship(
        secondary="project_skills", back_populates="projects")
    project_images: Mapped[list["ProjectImage"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectImage.display_order",
    )

