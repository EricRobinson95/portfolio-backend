from app.models.project_image import ProjectImage

from app.repositories.project_image_repository import (
    ProjectImageRepository,
)
from app.repositories.project_repository import (
    ProjectRepository,
)

from app.schemas.project_images import (
    ProjectImageCreate,
    ProjectImageUpdate,
)

from app.exceptions.project_image_exceptions import (
    DuplicateProjectImageDisplayOrderError,
    ProjectImageNotFoundError,
)
from app.exceptions.project_exceptions import (
    ProjectNotFoundError,
)


class ProjectImageService:
    def __init__(
        self,
        project_image_repository: ProjectImageRepository,
        project_repository: ProjectRepository,
    ):
        self.project_image_repository = project_image_repository
        self.project_repository = project_repository

    def create(
        self,
        project_image_create: ProjectImageCreate,
    ) -> ProjectImage:

        project = self.project_repository.get_by_id(
            project_image_create.project_id
        )
        if project is None:
            raise ProjectNotFoundError(
                project_image_create.project_id
            )

        if self.project_image_repository.exists(
            project_image_create.project_id,
            project_image_create.display_order,
        ):
            raise DuplicateProjectImageDisplayOrderError(
                project_image_create.display_order,
                project_image_create.project_id,
            )

        project_image = ProjectImage(
            project_id=project_image_create.project_id,
            title=project_image_create.title,
            description=project_image_create.description,
            image_url=project_image_create.image_url,
            display_order=project_image_create.display_order,
        )

        return self.project_image_repository.create(
            project_image
        )

    def get_by_id(
        self,
        project_image_id: int,
    ) -> ProjectImage:
        project_image = self.project_image_repository.get_by_id(
            project_image_id
        )
        if project_image is None:
            raise ProjectImageNotFoundError(
                project_image_id
            )
        return project_image

    def get_by_project_id(
        self,
        project_id: int,
    ) -> list[ProjectImage]:
        return self.project_image_repository.get_by_project_id(
            project_id
        )

    def update(
        self,
        project_image: ProjectImage,
        project_image_update: ProjectImageUpdate,
    ) -> ProjectImage:

        if (
            project_image_update.display_order is not None
            and project_image_update.display_order
            != project_image.display_order
        ):
            if self.project_image_repository.exists(
                project_image.project_id,
                project_image_update.display_order,
            ):
                raise DuplicateProjectImageDisplayOrderError(
                    project_image_update.display_order,
                    project_image.project_id,
                )

            project_image.display_order = (
                project_image_update.display_order
            )

        if project_image_update.title is not None:
            project_image.title = (
                project_image_update.title
            )

        if project_image_update.description is not None:
            project_image.description = (
                project_image_update.description
            )

        if project_image_update.image_url is not None:
            project_image.image_url = (
                project_image_update.image_url
            )

        return self.project_image_repository.update(
            project_image
        )

    def delete(
        self,
        project_image: ProjectImage,
    ) -> None:
        self.project_image_repository.delete(
            project_image
        )