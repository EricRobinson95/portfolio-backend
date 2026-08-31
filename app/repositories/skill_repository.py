from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.skill import Skill


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, skill: Skill) -> Skill:
        try:
            self.db.add(skill)
            self.db.commit()
            self.db.refresh(skill)
            return skill
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, skill_id: int) -> Skill | None:
        return self.db.get(Skill, skill_id)

    def get_all(self) -> list[Skill]:
        statement = select(Skill)
        result = self.db.execute(statement)
        return result.scalars().all()

    def get_by_name(self, name: str) -> Skill | None:
        statement = select(Skill).where(
            Skill.name == name
        )
        result = self.db.execute(statement)
        return result.scalars().one_or_none()

    def update(self, skill: Skill) -> Skill:
        try:
            self.db.commit()
            self.db.refresh(skill)
            return skill
        except Exception:
            self.db.rollback()
            raise

    def delete(self, skill: Skill) -> None:
        try:
            self.db.delete(skill)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise