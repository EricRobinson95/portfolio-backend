from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.technology import Technology


class TechnologyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, technology: Technology) -> Technology:
        self.db.add(technology)
        self.db.commit()
        self.db.refresh(technology)
        return technology

    def get_by_id(self, technology_id: int) -> Technology | None:
        return self.db.get(Technology, technology_id)

    def get_all(self) -> list[Technology]:
        statement = select(Technology)
        result = self.db.execute(statement)
        return result.scalars().all()

    def get_by_name(self, name: str) -> Technology | None:
        statement = select(Technology).where(
            Technology.name == name
        )
        result = self.db.execute(statement)
        return result.scalars().one_or_none()

    def update(self, technology: Technology) -> Technology:
        self.db.commit()
        self.db.refresh(technology)
        return technology

    def delete(self, technology: Technology) -> None:
        self.db.delete(technology)
        self.db.commit()