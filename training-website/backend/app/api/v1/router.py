from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse, tags=["system"])
def api_health() -> HealthResponse:
    return HealthResponse(status="ok", service="training-website", environment="development")
