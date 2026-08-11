from sqlalchemy.orm import Session

from app.database.database import SessionLocal

# =====================================================
# SQLAlchemy Models
# =====================================================

import app.models.project
import app.models.technology
import app.models.project_technology
import app.models.project_image
import app.models.skill
import app.models.project_skill

# =====================================================
# Seed Data
# =====================================================

from app.seeds.projects_seed import PROJECTS
from app.seeds.technologies_seed import TECHNOLOGIES
from app.seeds.skills_seed import SKILLS
from app.seeds.project_images_seed import PROJECT_IMAGES
from app.seeds.project_technologies_seed import PROJECT_TECHNOLOGIES
from app.seeds.project_skills_seed import PROJECT_SKILLS


def seed_database(db: Session) -> None:
    """
    Populate the database with the initial portfolio data.
    """

    # =====================================================
    # Projects
    # =====================================================

    for project in PROJECTS:
        db.add(project)

    db.flush()

    # =====================================================
    # Technologies
    # =====================================================

    for technology in TECHNOLOGIES:
        db.add(technology)

    db.flush()

    # =====================================================
    # Skills
    # =====================================================

    for skill in SKILLS:
        db.add(skill)

    db.flush()

    # =====================================================
    # Project Images
    # =====================================================

    for project_image in PROJECT_IMAGES:
        db.add(project_image)

    # =====================================================
    # Project Technologies
    # =====================================================

    for project_technology in PROJECT_TECHNOLOGIES:
        db.add(project_technology)

    # =====================================================
    # Project Skills
    # =====================================================

    for project_skill in PROJECT_SKILLS:
        db.add(project_skill)

    # =====================================================
    # Commit
    # =====================================================

    db.commit()


def main() -> None:
    """
    Create a database session and execute the seed operation.
    """

    db = SessionLocal()

    try:
        seed_database(db)
        print("Database seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()