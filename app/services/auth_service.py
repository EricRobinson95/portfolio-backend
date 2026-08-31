from fastapi import HTTPException, status

from app.core.security import verify_password, create_access_token
from app.repositories.admin_repository import AdminRepository


class AuthService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> str:
        admin = self.admin_repository.get_by_username(username)

        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not verify_password(password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        return create_access_token(admin.username)