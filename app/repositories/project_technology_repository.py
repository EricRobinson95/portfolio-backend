from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.project_technology import ProjectTechnology


class ProjectTechnologyRepository:
    def __init__(self, db: Session):
        self.db = db


    def exists(self, project_id:int, technology_id:int) -> bool:
        statement = select(ProjectTechnology).where(
            ProjectTechnology.project_id == project_id,
            ProjectTechnology.technology_id == technology_id
        )
        result = self.db.execute(statement)
        return result.scalars().first() is not None


    def create(self, project_id:int, technology_id:int) -> None:
        project_technology = ProjectTechnology(
            project_id=project_id,
            technology_id=technology_id
        )
        try:
            self.db.add(project_technology)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise


    def delete(self, project_id:int, technology_id:int) -> None:
        statement = select(ProjectTechnology).where(
            ProjectTechnology.project_id == project_id,
            ProjectTechnology.technology_id == technology_id
        )
        result = self.db.execute(statement)
        project_technology = result.scalars().first()
        try:
            self.db.delete(project_technology)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
