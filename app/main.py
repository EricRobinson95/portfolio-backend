from fastapi import FastAPI

from app.routers.project_router import router as project_router
from app.routers.technology_router import router as technology_router
from app.routers.skill_router import router as skill_router
from app.routers.project_image_router import router as project_image_router
from app.exceptions.exception_handlers import register_exception_handlers



app = FastAPI(
    title="Portfolio Backend API",
    description="Backend API for my developer portfolio.",
    version="1.0.0",
)
register_exception_handlers(app)
app.include_router(project_router)
app.include_router(technology_router)
app.include_router(skill_router)
app.include_router(project_image_router)

