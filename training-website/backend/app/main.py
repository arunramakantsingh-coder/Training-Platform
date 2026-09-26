from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "training-website", "environment": settings.app_env}

@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "training-website"}
