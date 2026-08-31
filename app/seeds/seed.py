from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.project import Project
from app.models.project_image import ProjectImage
from app.models.project_skill import ProjectSkill
from app.models.project_technology import ProjectTechnology
from app.models.skill import Skill
from app.models.technology import Technology
from app.seeds.project_images_seed import PROJECT_IMAGES
from app.seeds.project_skills_seed import PROJECT_SKILLS
from app.seeds.project_technologies_seed import PROJECT_TECHNOLOGIES
from app.seeds.projects_seed import PROJECTS
from app.seeds.skills_seed import SKILLS
from app.seeds.technologies_seed import TECHNOLOGIES


def seed_database(db: Session) -> dict[str, int]:
    """Create missing portfolio seed data without changing existing records."""
    created = defaultdict(int)

    projects: dict[int, Project] = {}
    for template_id, seed_project in enumerate(PROJECTS, start=1):
        project = db.scalar(
            select(Project).where(Project.title == seed_project.title)
        )
        if project is None:
            project = Project(
                title=seed_project.title,
                github_url=seed_project.github_url,
                image_thumbnail_url=seed_project.image_thumbnail_url,
                description=seed_project.description,
            )
            db.add(project)
            created["projects"] += 1
        projects[template_id] = project

    technologies: dict[int, Technology] = {}
    for template_id, seed_technology in enumerate(TECHNOLOGIES, start=1):
        technology = db.scalar(
            select(Technology).where(
                Technology.name == seed_technology.name
            )
        )
        if technology is None:
            technology = Technology(
                name=seed_technology.name,
                icon=seed_technology.icon,
                description=seed_technology.description,
            )
            db.add(technology)
            created["technologies"] += 1
        technologies[template_id] = technology

    skills: dict[int, Skill] = {}
    for template_id, seed_skill in enumerate(SKILLS, start=1):
        skill = db.scalar(select(Skill).where(Skill.name == seed_skill.name))
        if skill is None:
            skill = Skill(
                name=seed_skill.name,
                description=seed_skill.description,
            )
            db.add(skill)
            created["skills"] += 1
        skills[template_id] = skill

    db.flush()

    for seed_image in PROJECT_IMAGES:
        project = projects[seed_image.project_id]
        image = db.scalar(
            select(ProjectImage).where(
                ProjectImage.project_id == project.id,
                ProjectImage.display_order == seed_image.display_order,
            )
        )
        if image is None:
            db.add(
                ProjectImage(
                    project_id=project.id,
                    title=seed_image.title,
                    description=seed_image.description,
                    image_url=seed_image.image_url,
                    display_order=seed_image.display_order,
                )
            )
            created["project_images"] += 1

    for seed_relationship in PROJECT_TECHNOLOGIES:
        project = projects[seed_relationship.project_id]
        technology = technologies[seed_relationship.technology_id]
        relationship = db.get(
            ProjectTechnology,
            (project.id, technology.id),
        )
        if relationship is None:
            db.add(
                ProjectTechnology(
                    project_id=project.id,
                    technology_id=technology.id,
                )
            )
            created["project_technologies"] += 1

    for seed_relationship in PROJECT_SKILLS:
        project = projects[seed_relationship.project_id]
        skill = skills[seed_relationship.skill_id]
        relationship = db.get(ProjectSkill, (project.id, skill.id))
        if relationship is None:
            db.add(
                ProjectSkill(
                    project_id=project.id,
                    skill_id=skill.id,
                )
            )
            created["project_skills"] += 1

    db.commit()
    return dict(created)


def main() -> None:
    """Create missing seed data in the configured database."""

    db = SessionLocal()

    try:
        created = seed_database(db)
        if created:
            print(f"Database seeded. Created: {created}")
        else:
            print("Database already contains all seed data.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
