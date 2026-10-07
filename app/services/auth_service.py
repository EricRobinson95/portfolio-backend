from fastapi import HTTPException, status

from app.core.security import verify_password, create_access_token
from app.repositories.admin_repository import AdminRepository
from app.core.tracing import operation_span


class AuthService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> str:
        with operation_span("admin.authenticate") as auth_span:
            with operation_span("admin.lookup"):
                admin = self.admin_repository.get_by_username(username)

            if admin is None:
                auth_span.set_attribute("app.login.outcome", "rejected")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )

            with operation_span("admin.verify_password"):
                password_valid = verify_password(
                    password,
                    admin.password_hash,
                )

            if not password_valid:
                auth_span.set_attribute("app.login.outcome", "rejected")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )

            with operation_span("admin.create_token"):
                access_token = create_access_token(admin.username)

            auth_span.set_attribute("app.login.outcome", "success")
            return access_token
