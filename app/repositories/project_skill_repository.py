from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.project_skill import ProjectSkill


class ProjectSkillRepository:
    def __init__(self, db: Session):
        self.db = db


    def exists(self, project_id:int, skill_id:int) -> bool:
        statement = select(ProjectSkill).where(
            ProjectSkill.project_id == project_id,
            ProjectSkill.skill_id == skill_id
        )
        result = self.db.execute(statement)
        return result.scalars().first() is not None


    def create(self, project_id:int, skill_id:int) -> None:
        project_skill = ProjectSkill(
            project_id=project_id,
            skill_id=skill_id
        )
        try:
            self.db.add(project_skill)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise


    def delete(self, project_id:int, skill_id:int) -> None:
        statement = select(ProjectSkill).where(
            ProjectSkill.project_id == project_id,
            ProjectSkill.skill_id == skill_id
        )
        result = self.db.execute(statement)
        project_skill = result.scalars().first()
        try: 
            self.db.delete(project_skill)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
