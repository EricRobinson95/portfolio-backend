from fastapi import Depends

from app.dependencies.admin_dependencies import get_admin_repository
from app.repositories.admin_repository import AdminRepository
from app.services.auth_service import AuthService


def get_auth_service(
    admin_repository: AdminRepository = Depends(
        get_admin_repository
    ),
) -> AuthService:
    return AuthService(admin_repository)