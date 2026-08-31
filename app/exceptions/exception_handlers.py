from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.project_exceptions import DuplicateProjectTitleError, ProjectNotFoundError
from app.exceptions.project_technology_exceptions import ProjectTechnologyAlreadyExistsError, ProjectTechnologyNotFoundError
from app.exceptions.technology_exception import DuplicateTechnologyNameError, TechnologyNotFoundError
from app.exceptions.skill_exceptions import SkillNotFoundError, DuplicateSkillNameError
from app.exceptions.project_image_exceptions import ProjectImageNotFoundError, DuplicateProjectImageDisplayOrderError
from app.exceptions.project_skill_exceptions import ProjectSkillAlreadyExistsError, ProjectSkillNotFoundError

def register_exception_handlers(app: FastAPI):

    @app.exception_handler(DuplicateProjectTitleError)
    async def duplicate_project_title_handler(
        request: Request,
        exc: DuplicateProjectTitleError,
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )


    @app.exception_handler(ProjectNotFoundError)
    async def project_not_found_handler(
        request: Request,
        exc: ProjectNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )


    @app.exception_handler(DuplicateTechnologyNameError)
    async def duplicate_technology_name_handler(
        request: Request,
        exc: DuplicateTechnologyNameError,
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(TechnologyNotFoundError)
    async def technology_not_found_handler(
        request: Request,
        exc: TechnologyNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ProjectTechnologyAlreadyExistsError)
    async def project_technology_already_exists_handler(
        request: Request,
        exc: ProjectTechnologyAlreadyExistsError,
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ProjectTechnologyNotFoundError)
    async def project_technology_not_found_handler(
        request: Request,
        exc: ProjectTechnologyNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateSkillNameError)
    async def duplicate_skill_name_handler(
        request: Request,
        exc: DuplicateSkillNameError,
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SkillNotFoundError)
    async def skill_not_found_handler(
        request: Request,
        exc: SkillNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},)

    @app.exception_handler(ProjectSkillAlreadyExistsError)
    async def project_skill_already_exists_handler(
    request: Request,
    exc: ProjectSkillAlreadyExistsError,
        ):
        return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},)


    @app.exception_handler(ProjectSkillNotFoundError)
    async def project_skill_not_found_handler(
    request: Request,
    exc: ProjectSkillNotFoundError,
        ):
        return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},)


    @app.exception_handler(ProjectImageNotFoundError)
    async def project_image_not_found_handler(
        request: Request,
        exc: ProjectImageNotFoundError,
        ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},)

    @app.exception_handler(DuplicateProjectImageDisplayOrderError)
    async def duplicate_project_image_display_order_handler(
        request: Request,
        exc: DuplicateProjectImageDisplayOrderError,
        ):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},)

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )
