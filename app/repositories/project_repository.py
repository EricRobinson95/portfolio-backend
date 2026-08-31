from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        try:
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            return project
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, project_id: int) -> Project | None:
        return self.db.get(Project, project_id)

    def get_all(self) -> list[Project]:
        statement = select(Project)
        results = self.db.execute(statement)
        return results.scalars().all()

    def get_by_title(self, title: str) -> Project | None:
        statement = select(Project).where(
            Project.title == title
        )
        results = self.db.execute(statement)
        return results.scalars().one_or_none()

    def update(self, project: Project) -> Project:
        try:
            self.db.commit()
            self.db.refresh(project)
            return project
        except Exception:
            self.db.rollback()
            raise

    def delete(self, project: Project) -> None:
        try:
            self.db.delete(project)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise