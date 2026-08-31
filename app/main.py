from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.project_router import router as project_router
from app.routers.technology_router import router as technology_router
from app.routers.skill_router import router as skill_router
from app.routers.project_image_router import router as project_image_router
from app.routers.auth_router import router as auth_router
from app.routers.health_router import router as health_router
from app.exceptions.exception_handlers import register_exception_handlers
from fastapi.staticfiles import StaticFiles
from app.core.config import settings


app = FastAPI(
    title="Portfolio Backend API",
    description="Backend API for my developer portfolio.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://10.0.0.236:3000"
        ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.should_serve_local_static_files:
    app.mount(
        "/static",
        StaticFiles(directory="app/static"),
        name="static",
    )

register_exception_handlers(app)
app.include_router(project_router)
app.include_router(technology_router)
app.include_router(skill_router)
app.include_router(project_image_router)
app.include_router(auth_router)
app.include_router(health_router)

