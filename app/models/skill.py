from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.database.database import Base
if TYPE_CHECKING:
    from app.models.project import Project





class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),
                                    unique=True)
    description: Mapped[str] = mapped_column(String(250))
    projects: Mapped[list["Project"]] = relationship(
        secondary="project_skills", back_populates="skills"
    )
