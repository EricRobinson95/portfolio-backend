from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_image import ProjectImage


class ProjectImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_image: ProjectImage) -> ProjectImage:
        self.db.add(project_image)
        self.db.commit()
        self.db.refresh(project_image)
        return project_image

    def get_by_id(self, project_image_id: int) -> ProjectImage | None:
        return self.db.get(ProjectImage, project_image_id)

    def get_by_project_id(self,project_id: int,) -> list[ProjectImage]:
        statement = (select(ProjectImage).where(
            ProjectImage.project_id == project_id).order_by(
                ProjectImage.display_order
            )

            )
        results = self.db.execute(statement)
        return results.scalars().all()

    def exists(self, project_id:int, display_order:int) -> bool:
        statement = select(ProjectImage).where(
            ProjectImage.project_id == project_id,
            ProjectImage.display_order == display_order
            )
        result = self.db.execute(statement)
        return result.scalars().first() is not None

    def update(self, project_image: ProjectImage) -> ProjectImage:
        self.db.commit()
        self.db.refresh(project_image)
        return project_image

    def delete(self, project_image: ProjectImage) -> None:
        self.db.delete(project_image)
        self.db.commit()