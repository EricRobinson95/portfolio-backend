from fastapi import APIRouter, Depends

from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.auth_service_dependencies import get_auth_service
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    access_token = service.authenticate(
        login_request.username,
        login_request.password,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/test")
def test_authentication(
    current_user: str = Depends(get_current_user),
):
    return {
        "authenticated": True,
        "user": current_user,
    }