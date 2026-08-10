from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
if TYPE_CHECKING:
    from app.models.project import Project




class Technology(Base):
    __tablename__ = "technologies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),
                                    unique=True)
    icon: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(250))
    projects: Mapped[list["Project"]] = relationship(
        secondary="project_technologies", back_populates="technologies"
    )