from fastapi import APIRouter


router = APIRouter(
    tags=["health"],
)


@router.get("/health")
def health_check() -> dict[str, str]:
    """Report that the API process is able to respond to requests."""
    return {"status": "ok"}
