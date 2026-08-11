from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database.database import Base
if TYPE_CHECKING:
    from app.models.project import Project




class ProjectImage(Base):
    __tablename__ = "project_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column( ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(200))
    display_order: Mapped[int] = mapped_column()
    project: Mapped["Project"] = relationship(
        back_populates="project_images"
    )